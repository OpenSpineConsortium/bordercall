#include <unistd.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char **argv) {
  char **args = calloc(argc + 4, sizeof(char *));
  args[0] = "/lib64/ld-linux-x86-64.so.2";
  args[1] = "--library-path";
  args[2] = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/skeptic-tests-words/c7/lib2";
  args[3] = REAL;
  for (int i = 1; i < argc; i++) args[i + 3] = argv[i];
  execv(args[0], args);
  return 127;
}
