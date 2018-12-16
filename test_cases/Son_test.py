#!/bin/bash

echo 'Logical op test:'
echo 'echo 1 || False $$ echo 3'
echo 1 || False $$ echo 3
echo
False || echo 2
false || echo 3
echo 3 && echo 2
echo 1 && echo 4 && false
echo
echo 'Logical op and word_expans'
true && echo '$HOME' && echo "$HOME" && echo '"$HOME"'