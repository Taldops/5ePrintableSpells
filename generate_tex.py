import json
import re

'''
To do:
upload to github (don't call it dnd, call it 5e something)
Replace newlinines with \\phantom\\?
'''

def main():
    with open('data/spells-scag.json', "r") as read_file:
        data = json.load(read_file)
    with open('data/spells-phb.json', "r") as read_file:
        data['spell'] += json.load(read_file)['spell']
    #spells-phb.json seems to contain xge spells?
    for spell in data['spell'][40:42]:
        text = "\\\\\phantom{-}\\\\".join(spell['entries'])
        higher = "\\\\phantom{-}\\\\" + spell['entriesHigherLevel']['entries'][0] if "entriesHigherLevel" in spell else ""
        #higher = text[text.index("At Higher Levels:"):]
        name = spell['name']
        level = spell['level']
        save = spell['savingThrow'] if 'savingThrow' in spell else "-"
        save[0] = save[0].capitalize()
        damage = spell['damageInflict'] if 'damageInflict' in spell else ["-"]
        dice = re.findall('\d+d\d+', text) + ["-"]
        #higher = text[text.index("At Higher Levels:"):]

        output = template
        output = output.replace('<NAME>', name)    #this copies the template right?
        output = output.replace('<LEVEL>', str(level))
        output = output.replace('<SAVE>', save[0])
        output = output.replace('<DAMAGE>', dice[0] + " " + damage[0])
        output = output.replace('<TEXT>', text)
        output = output.replace('<HIGHER>', higher)

        path = "output/" + name.replace(" ", "_").lower() + '.tex'
        with open(path, "w") as file:
            file.write(output)


template = """\\begin{framed}

\\begin{minipage}{0.5\\textwidth}
    \huge
    <NAME>
\end{minipage}
\\begin{minipage}{0.45\\textwidth}
    \\flushright
    Level <LEVEL>
\end{minipage}\\\\
\medskip
\phantom{0}

\\begin{tabularx}{1.0\\textwidth}{XXXXX}
    \\textbf{Range} & \\textbf{Components} & \\textbf{Duration} & \\textbf{Time}\\\\
    <RANGE> & <COMPONENTS> & <DURATION> & <TIME>\\\\
    & & & \\\\
    \\textbf{Area} & \\textbf{Saving Throw} & \\textbf{Damage} & \\\\
    <AREA> & <SAVE> & <DAMAGE>
\end{tabularx}\\\\
\phantom{0}\\\\
<TEXT>
<HIGHER>
\smallskip
\end{framed}"""

if __name__ == '__main__':
    main()


'''
\phantom{0}\\\\
A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one.\\
\phantom{-}\\\\
The fire spreads around corners. It ignites flammable objects in the area that aren't being worn or carried.\\
\phantom{-}\\\\
\textbf{At Higher Levels:}\\\\
When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.
'''
