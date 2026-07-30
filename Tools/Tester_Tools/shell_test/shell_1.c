#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_LINE 80    /* The maximum length command */
#define MAX_ARGS (MAX_LINE/2 + 1)

int main(void) {
    char *args[MAX_ARGS]; /* Command line arguments */
    char inputBuffer[MAX_LINE];
    int should_run = 1;   /* Flag to determine when to exit */
    
    while (should_run) {
        printf("myshell> ");
        fflush(stdout);
        
        /* Read user input */
        if (fgets(inputBuffer, MAX_LINE, stdin) == NULL) {
            break;
        }
        
        /* Remove newline character */
        inputBuffer[strcspn(inputBuffer, "\n")] = '\0';
        
        /* Parse the input string into arguments */
        int i = 0;
        char *token = strtok(inputBuffer, " ");
        while (token != NULL) {
            args[i++] = token;
            token = strtok(NULL, " ");
        }
        args[i] = NULL; /* Null-terminate the argument array */
        
        /* If no command entered, skip loop */
        if (args[0] == NULL) {
            continue;
        }
        
        /* Built-in exit command */
        if (strcmp(args[0], "exit") == 0) {
            should_run = 0;
            continue;
        }
        
        /* Fork a child process to run the command */
        pid_t pid = fork();
        
        if (pid < 0) {
            /* Error occurred */
            fprintf(stderr, "Fork Failed\n");
            return 1;
        } 
        else if (pid == 0) {
            /* Child process: execute the command */
            if (execvp(args[0], args) < 0) {
                printf("Command not found\n");
                exit(1);
            }
        } 
        else {
            /* Parent process: wait for child to complete */
            wait(NULL);
        }
    }
    return 0;
}
