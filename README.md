# 5ePrintableSpells
This program generates LaTeX code for all spells and their descriptions in 5e. You can use this to make a printable document with any collection of spells.

This is a work in progress. Some spells will probably have mistakes and formatting errors in them, so you should probably double check your selection.

## Instructions
1. Download the repository.
2. Download the the spell data from [here](https://github.com/TheGiddyLimit/TheGiddyLimit.github.io/tree/master/data/spells) . Place all the *.json* files in the data folder.
3. Run *generate_tex.py*. This will produce one *.tex* file for each spell. You'll find those in the output folder.
4. You can now use the spells in a Latex, either by copy-pasting the content or by using `\include{output/<spell_name>.tex}`. See *example.tex*.
5. Some spells might contain errors. You will have to fix them manually in the corresponding *.tex* file or write a fix into the script itself and submit a pull request.

## To do
 - Display material components with a cost
 - Better damage display for scaling cantrips
 - Prettier tables
 - Use colors to highlight important aspects
