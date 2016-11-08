[![Build Status](https://travis-ci.org/lasote/conan-libjpeg-turbo.svg)](https://travis-ci.org/lasote/conan-libjpeg-turbo)


# conan-libjpeg-turbo

[Conan.io](https://conan.io) package for lib libjpeg-turbo library.

Thanks to @a-teammate for his contribution.

The packages generated with this **conanfile** can be found in [conan.io](https://conan.io/source/libjpeg-turbo/1.5.1/lasote/stable).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

## Upload packages to server

    $ conan upload libjpeg-turbo/1.5.1@lasote/stable --all
    
## Reuse the packages

### Basic setup

    $ conan install libjpeg-turbo/1.5.1@lasote/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    libjpeg-turbo/1.5.1@lasote/stable

    [options]
    libjpeg-turbo:shared=true # false
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.

