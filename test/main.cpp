#include <stdio.h>
#include <string.h>
#include "jpeglib.h"
#include <iostream>

int return_value = 1;
// JPEG error handler
void JPEGVersionError(j_common_ptr cinfo)
 {
   int jpeg_version = cinfo->err->msg_parm.i[0];
   std::cout << "JPEG version: " << jpeg_version << std::endl;
   return_value = 0;
 }

int main()
{
  // Need to construct a decompress struct and give it an error handler
  // by passing an invalid version number we always trigger an error
  // the error returns the linked version number as the first integer parameter
  jpeg_decompress_struct cinfo;
  jpeg_error_mgr error_mgr;
  error_mgr.error_exit = &JPEGVersionError;
  cinfo.err = &error_mgr;
  jpeg_CreateDecompress(&cinfo, -1 /*version*/, sizeof(cinfo)); // Pass -1 to always force an erro

  return return_value;
}