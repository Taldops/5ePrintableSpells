import json
import re

'''
To do:
upload to github (don't call it dnd, call it 5e something)
Replace newlinines with \\phantom\\?
'''
def clean_text(text):
    text = text.replace('@condition ', '')
    text = text.replace('@dice ', '')
    return text

def get_damage(spell):
    text = "".join(spell['entries'])    #TODO this is done again to avoid extra parameters. Refactor this, so it is only done once!
    damage = spell['damageInflict'] if 'damageInflict' in spell else ["-"]
    dice = re.findall('\d+d\d+', text) + ["-"]
    if len(dice) > 2:
        dice = "Varies"
    else:
        dice = dice[0]
    if len(damage) > 1:
        if dice == "Varies":
            damage = ""
        else:
            damage = "various"
    else:
        damage = damage[0]
        if dice == "Varies":
            damage = "(" + damage + ")"
    return dice, damage

def main():
    with open('template.tex', "r") as read_file:
        template = "".join(read_file.readlines())
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
        range = str(spell['range']['distance']['amount']) + " " + spell['range']['distance']['type']
        components = ", ".join(list(zip(*list(spell['components'].items())))[0]).upper()
        save = spell['savingThrow'] if 'savingThrow' in spell else ""
        if len(spell['duration']) > 1:
            print(name, "has multiple durations")
        time = str(spell['time'][0]['number']) + " " + spell['time'][0]['unit']
        duration = str(spell['duration'][0]['duration']['amount']) + " " + spell['duration'][0]['duration']['type']
        if spell['duration'][0]['concentration']:
            duration = "(C) " + duration
        if type(save) == list:
            save = ", ".join(save)
        save = save.capitalize()
        dice, damage = get_damage(spell)

        #higher = text[text.index("At Higher Levels:"):]
        text = clean_text(text)
        output = template
        output = output.replace('<NAME>', name)    #this copies the template right?
        output = output.replace('<LEVEL>', str(level))
        output = output.replace('<RANGE>', range)
        output = output.replace('<COMPONENTS>', components)
        output = output.replace('<DURATION>', duration)
        output = output.replace('<TIME>', time)
        output = output.replace('<SAVE>', save)
        output = output.replace('<DAMAGE>', dice + " " + damage)
        output = output.replace('<TEXT>', text)
        output = output.replace('<HIGHER>', higher)

        path = "output/" + name.replace(" ", "_").lower() + '.tex'
        with open(path, "w") as file:
            file.write(output)

if __name__ == '__main__':
    main()
