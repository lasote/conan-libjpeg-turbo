from conans import ConanFile, ConfigureEnvironment
import os
from conans.tools import download
from conans.tools import unzip, replace_in_file
from conans import CMake


class LibJpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    version = "1.4.2"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports = "CMakeLists.txt"
    url="http://github.com/lasote/libjpeg-turbo"
    license="https://github.com/libjpeg-turbo/libjpeg-turbo/blob/1.4.2/LICENSE.txt"
    
       
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

        if self.settings.os == "Linux" or self.settings.os == "Macos":            
            self.run("cd %s && autoreconf -fiv" % self.ZIP_FOLDER_NAME)
            config_options = ""
            if self.settings.arch == "x86":
                if self.settings.os == "Linux":
                    config_options = "--host i686-pc-linux-gnu CFLAGS='-O3 -m32' LDFLAGS=-m32"
                else:
                    config_options = "--host i686-apple-darwin CFLAGS='-O3 -m32' LDFLAGS=-m32"

            self.run("cd %s && %s ./configure %s" % (self.ZIP_FOLDER_NAME, env.command_line, config_options))
            self.run("cd %s && %s make" % (self.ZIP_FOLDER_NAME, env.command_line))
        else:
            conan_magic_lines = '''project(libjpeg-turbo)
    cmake_minimum_required(VERSION 3.0)
    include(../conanbuildinfo.cmake)
    CONAN_BASIC_SETUP()
    '''
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "cmake_minimum_required(VERSION 2.8.8)", conan_magic_lines)
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "project(libjpeg-turbo C)", "")
            
            cmake = CMake(self.settings)
            self.run("cd %s && mkdir _build" % self.ZIP_FOLDER_NAME)
            cd_build = "cd %s/_build" % self.ZIP_FOLDER_NAME
            self.run('%s && cmake .. %s' % (cd_build, cmake.command_line))
            self.run("%s && cmake --build . %s" % (cd_build, cmake.build_config))
                
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
            self.copy(pattern="*.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
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
            self.cpp_info.libs = ['libturbojpeg']
        else:
            self.cpp_info.libs = ['turbojpeg']
