from conans import ConanFile, ConfigureEnvironment
import os
from conans.tools import download
from conans.tools import unzip, replace_in_file
from conans import CMake
import shutil, sys


class LibJpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    version = "1.4.2"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "SSE": [True, False]}
    default_options = "shared=False", "fPIC=True", "SSE=True"
    exports = "CMakeLists.txt"
    url="http://github.com/lasote/conan-libjpeg-turbo"
    license="https://github.com/libjpeg-turbo/libjpeg-turbo/blob/1.4.2/LICENSE.txt"
    
    def config(self):
        del self.settings.compiler.libcxx # pure c lib
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
       
    def source(self):
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
        download("http://downloads.sourceforge.net/project/libjpeg-turbo/%s/%s" % (self.version, zip_name), zip_name)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)

        set_path_command = ""
        # Download nasm as build tool. This should go to source()
        if self.options.SSE == True:
            if self.settings.os == "Linux":
                # TODO: We should build nasm from source then.
                self.options.SSE = False # Or is removing here better? I'm not familiar with python..
            else:
                nasm_version = "2.12.02"
                nasm_os_url_id = "" #nasm url identifier
                if self.settings.os == "Windows":
                    if self.settings.arch == "x86":
                        nasm_os_url_id = "win32"
                    else:
                        nasm_os_url_id = "win64" 
                elif self.settings.os == "Macos":
                    nasm_os_url_id = "macosx"
                nasm_folder_name = "nasm-%s-%s" % (nasm_version, nasm_os_url_id)
                nasm_zip_name = "%s.zip" % nasm_folder_name
                download("http://www.nasm.us/pub/nasm/releasebuilds/%s/%s/%s" % (nasm_version, nasm_os_url_id, nasm_zip_name), nasm_zip_name)
                self.output.warn("Downloading nasm: http://www.nasm.us/pub/nasm/releasebuilds/%s/%s/%s" % (nasm_version, nasm_os_url_id, nasm_zip_name))
                unzip(nasm_zip_name)
                os.unlink(nasm_zip_name)
                nasm_path = os.path.join(os.getcwd(), nasm_folder_name)

                #env.environ["PATH"] += os.pathsep + nasm_path #its probably as easy as this, but i cant append to the path self.run operates in.
                if self.settings.os == "Windows":
                    set_path_command = "set \"PATH=%s\" &&" % os.environ["PATH"]
                else:
                    set_path_command = "PATH=\"%s\" &&" % os.environ["PATH"]

        if self.settings.os == "Linux" or self.settings.os == "Macos":
            if self.options.fPIC:
                env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
            else:
                env_line = env.command_line
            self.run("cd %s && autoreconf -fiv" % self.ZIP_FOLDER_NAME)
            config_options = ""
            if self.settings.arch == "x86":
                if self.settings.os == "Linux":
                    config_options = "--host i686-pc-linux-gnu CFLAGS='-O3 -m32' LDFLAGS=-m32"
                else:
                    config_options = "--host i686-apple-darwin CFLAGS='-O3 -m32' LDFLAGS=-m32"

            if self.settings.os == "Macos":
                old_str = '-install_name \$rpath/\$soname'
                new_str = '-install_name \$soname'
                replace_in_file("./%s/configure" % self.ZIP_FOLDER_NAME, old_str, new_str)

            self.run("cd %s && %s ./configure %s" % (self.ZIP_FOLDER_NAME, env_line, config_options))
            self.run("cd %s && %s make" % (self.ZIP_FOLDER_NAME, env_line))
        else: # We should (for simplicity) always use cmake shouldnt we?
            conan_magic_lines = '''project(libjpeg-turbo)
    cmake_minimum_required(VERSION 3.0)
    include(../conanbuildinfo.cmake)
    CONAN_BASIC_SETUP()
    '''
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "cmake_minimum_required(VERSION 2.8.8)", conan_magic_lines)
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "project(libjpeg-turbo C)", "")
            
            cmake = CMake(self.settings)
            builddir = os.path.join(self.ZIP_FOLDER_NAME, "_build")

            if os.path.exists(builddir):
                shutil.rmtree(builddir) # We need to remove this folder first for windows
            os.makedirs(builddir)

            cmake_options = []
            if self.options.shared == True:
                cmake_options += ["-DENABLE_STATIC=0"]
            else:
                cmake_options = ["-DENABLE_SHARED=0"]
            cmake_options += ["-DWITH_SIMD=%s" % "1" if self.options.SSE else "0"]

             # why this comment: "Don't change runtime, conan will take care of"? conan_basic_setup() runs before this cmake option replaces MT with MD again
            cmake_options += ["-DWITH_CRT_DLL=%s" % "1" if self.settings.compiler.runtime == "MD" or self.settings.compiler.runtime == "MDd" else "0"]

            self.run('%s cd %s && cmake .. %s %s' % (set_path_command, builddir, cmake.command_line, " ".join(cmake_options)))
            self.run("%s cd %s && cmake --build . %s" % (set_path_command, builddir, cmake.build_config))

    def package(self):
        """ Define your conan structure: headers, libs, bins and data. After building your
            project, this method is called to create a defined structure:
        """
        # Copying headers
        self.copy("*.h", "include", "%s" % (self.ZIP_FOLDER_NAME), keep_path=False)

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="*turbojpeg.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="*jpeg.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*jpeg-static.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.libs = ['jpeg', 'turbojpeg']
            else:
                self.cpp_info.libs = ['jpeg-static', 'turbojpeg-static']
        else:
            self.cpp_info.libs = ['jpeg', 'turbojpeg']


