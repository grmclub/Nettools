#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_LINE 1024
#define MAX_ARGS 64

// 1. Read input command line
char *read_line(void) {
    char *line = NULL;
    size_t bufsize = 0;
    if (getline(&line, &bufsize, stdin) == -1) {
        if (feof(stdin)) exit(EXIT_SUCCESS); // Handle Ctrl+D (EOF)
        perror("read line error");
        exit(EXIT_FAILURE);
    }
    return line;
}

// 2. Tokenize input string into arguments
char **parse_line(char *line) {
    int bufsize = MAX_ARGS, position = 0;
    char **tokens = malloc(bufsize * sizeof(char*));
    char *token;

    token = strtok(line, " \t\r\n\a");
    while (token != NULL) {
        tokens[position++] = token;
        token = strtok(NULL, " \t\r\n\a");
    }
    tokens[position] = NULL; // Null-terminate array of args
    return tokens;
}

// 3. Launch process using fork() and exec()
int launch_process(char **args) {
    pid_t pid;
    int status;

    pid = fork(); // Clone the process
    
    if (pid == 0) {
        // --- Child Process ---
        if (execvp(args[0], args) == -1) {
            perror("Shell error");
        }
        exit(EXIT_FAILURE);
    } else if (pid < 0) {
        // --- Forking Error ---
        perror("Fork failed");
    } else {
        // --- Parent Process ---
        // Block until child finishes
        do {
            waitpid(pid, &status, WUNTRACED);
        } while (!WIFEXITED(status) && !WIFSIGNALED(status));
    }

    return 1;
}

// Shell REPL (Read-Eval-Print Loop)
int main(int argc, char **argv) {
    char *line;
    char **args;
    int status = 1;

    while (status) {
        printf("my_shell> ");
        fflush(stdout);

        line = read_line();
        args = parse_line(line);

        if (args[0] != NULL) {
            // Built-in exit command check
            if (strcmp(args[0], "exit") == 0) {
                status = 0;
            } else {
                status = launch_process(args);
            }
        }

        free(line);
        free(args);
    }

    return 0;
}
