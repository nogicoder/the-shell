#!/bin/sh

echo AKSD$JKJB{ANSD}NKN*ABJSD_ABdsd
#expected: AKSD{ANSD}NKN*ABJSD_ABdsd
echo AKSD$JKJB${ANSD}NKN*ABJSD_ABdsd
#expected: AKSDNKN*ABJSD_ABdsd
echo AKSD$JKJB${ANS*D}NKN*ABJSD_ABdsd
#expected: bash: AKSD$JKJB${ANS*D}NKN*ABJSD_ABdsd: bad substitution
echo $NKSN_JASD+ASN${asdn+sk}nasnn
#expected: +ASNnasnn
echo $HOME=~/:~-/
#expected: /home/an=/home/an/:/home/an/
echo $HOME=~/:~+/
#expected: /home/an=/home/an/:/home/an/the-shell/
echo $HOM=$NKNL+ADKN_ABSDBK${PWD}N=~/
#expected: =+ADKN_ABSDBK/home/an/the-shellN=~/
