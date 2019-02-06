# 5ePrintableSpells
This program generates LaTeX code for all spells and their descriptions in 5e. You can easily make a list of spells in a printer friendly format with this.

## Instructions
1. Download the repository.
2. Download the the spell data from [here](https://github.com/TheGiddyLimit/TheGiddyLimit.github.io/tree/master/data/spells) . Place all the *.json* files in the data folder.
3. Run *generate_tex.py*. This will produce one *.tex* file for each spell. You'll find those in the output folder.
4. You can now use the spells in a Latex, either by copy-pasting the content or by using `\include{output/<spell_name>.tex}`. See *example.tex*.

## To do
 - Prettier tables
 - Colors
