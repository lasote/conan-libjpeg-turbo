#include <jversion.h>
#include <iostream>       // std::cout
#include <string>         // std::string

int main(){

  std::string str(JCOPYRIGHT_SHORT);
  std::string str2("The libjpeg-turbo Project");

  // different member versions of find in the same order as above:
  std::size_t found = str.find(str2);
  if (found!=std::string::npos)
    std::cout << str << std::endl;
    return 0;
  return 1;
}