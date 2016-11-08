from conans import ConanFile, ConfigureEnvironment
import os
from conans.tools import download
from conans.tools import unzip, replace_in_file
from conans import CMake


class LibJpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    version = "1.5.1"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "SSE": [True, False]}
    default_options = "shared=False", "fPIC=True", "SSE=True"
    exports = "CMakeLists.txt"
    url="http://github.com/lasote/libjpeg-turbo"
    license="https://github.com/libjpeg-turbo/libjpeg-turbo/blob/%s/LICENSE.txt" % version
    
    def config(self):
        try: # Try catch can be removed when conan 0.8 is released
            del self.settings.compiler.libcxx 
        except: 
            pass
        
        if self.settings.os == "Windows":
            self.requires.add("nasm/2.12.02@lasote/stable")
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
        env = ConfigureEnvironment(self)

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
        else:
            conan_magic_lines = '''project(libjpeg-turbo)
    cmake_minimum_required(VERSION 3.0)
    include(../conanbuildinfo.cmake)
    CONAN_BASIC_SETUP()
    '''
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "cmake_minimum_required(VERSION 2.8.8)", conan_magic_lines)
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "project(libjpeg-turbo C)", "")
            
            cmake_options = ["-DWITH_CRT_DLL=ON"]
            if self.options.shared == True:
                cmake_options.append("-DENABLE_STATIC=0 -DENABLE_SHARED=1")
            else:
                cmake_options.append("-DENABLE_SHARED=0 -DENABLE_STATIC=1")
            cmake_options.append("-DWITH_SIMD=%s" % "1" if self.options.SSE else "0")
            
            cmake = CMake(self.settings)
            self.run("cd %s && mkdir _build" % self.ZIP_FOLDER_NAME)
            cd_build = "cd %s/_build" % self.ZIP_FOLDER_NAME
             # Don't change runtime, conan will take care of, because conan already set the c/cpp flags, we dont need to change them
            self.run('%s && %s && cmake .. %s %s' % (env.command_line, cd_build, cmake.command_line, " ".join(cmake_options)))
            self.run("%s && %s && cmake --build . %s" % (env.command_line, cd_build, cmake.build_config))
                
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
