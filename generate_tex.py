import json
import re

'''
To do:
Work on area
'''

vprint = print if "--debug" in sys.argv or "--verbose" in sys.argv else lambda *a, **k: None

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

def find_area(text):
    #cone:
    if 'cone' in text:
        area = re.findall('\d+-foot cone', text)
        area = area.replace('-foot', 'ft')
    #sphere:
    elif 'sphere' in text:
        area = re.findall('\d+-[a-z]+-radius sphere', text)
        area = area.replace('-foot', 'ft')
        area = area[:-7]
    #cube:
    elif 'cube' in text:
        area = re.findall('\d+-[a-z]+-cube', text)
        area = area.replace('-foot', 'ft')
    #line:
    elif 'long line' in text or 'wide line' in text:
        area = re.findall('\d+-[a-z]+-wide, \d+-[a-z]+-long line', text)
        area += re.findall('\d+-[a-z]+-long, \d+-[a-z]+-wide line', text)
        dim = re.findall('\d+-[a-z]+', area)
        area = re.findall('\d+' in dim[0])[0] + re.findall('[a-z]+' in dim[0])[0]
        area += + " $\\times$ " + re.findall('\d+' in dim[1])[0] + re.findall('[a-z]+' in dim[1])[0]
        area += " line"
        area = area.replace('-foot', 'ft')
        #5-foot-wide, 60-foot-long line
    else:
        area = "-"
    return area

def main():
    with open('template.tex', "r") as read_file:
        template = "".join(read_file.readlines())
    with open('data/spells-scag.json', "r") as read_file:
        data = json.load(read_file)
    with open('data/spells-phb.json', "r") as read_file:
        data['spell'] += json.load(read_file)['spell']
    #spells-phb.json seems to contain xge spells?
    for spell in data['spell']:#[40:42]:
        text = "\\\\\\phantom{-}\\\\".join(spell['entries'])
        higher = "\\\\\\phantom{-}\\\\" + spell['entriesHigherLevel'][0]['entries'][0] if "entriesHigherLevel" in spell else ""
        #higher = text[text.index("At Higher Levels:"):]
        name = spell['name']
        level = spell['level']
        range = spell['range']['distance']['type']
        if 'amount' in spell['range']['distance']:
            range = str(spell['range']['distance']['amount']) + " " + range
        range = range.capitalize()
        components = ", ".join(list(zip(*list(spell['components'].items())))[0]).upper()
        save = spell['savingThrow'] if 'savingThrow' in spell else "-"
        if len(spell['duration']) > 1:
            print(name, "has multiple durations")
        time = str(spell['time'][0]['number']) + " " + spell['time'][0]['unit']
        duration = str(spell['duration'][0]['duration']['amount']) + " " + spell['duration'][0]['duration']['type']
        if 'concentration' in spell['duration'][0] and spell['duration'][0]['concentration']:
            duration = "(C) " + duration
        if type(save) == list:
            save = ", ".join(save)
        save = save.capitalize()
        dice, damage = get_damage(spell)
        area = find_area(text)

        #higher = text[text.index("At Higher Levels:"):]
        text = clean_text(text)
        output = template
        output = output.replace('<NAME>', name)    #this copies the template right?
        output = output.replace('<LEVEL>', str(level))
        output = output.replace('<RANGE>', range)
        output = output.replace('<AREA>', area)
        output = output.replace('<COMPONENTS>', components)
        output = output.replace('<DURATION>', duration)
        output = output.replace('<TIME>', time)
        output = output.replace('<SAVE>', save)
        output = output.replace('<TEXT>', text)
        output = output.replace('<HIGHER>', higher)

        #clean up
        delete = 0
        if dice + " " + damage == "- -":
            output = output.replace("\\textbf{Damage}", " ")
            output = output.replace('<DAMAGE>', " ")
            delete += 1
        else:
            output = output.replace('<DAMAGE>', dice + " " + damage)
        if save == "-":
            output = output.replace("\\textbf{Saving Throw}", " ")
            delete += 1
        if area == "-":
            #output = output.replace("\\textbf{Area}", " ")
            delete += 1
        #remove empty table rows:
        if delete == 3:
            begin = output.index("%d_begin")
            end = output.index("%d_end")
            output = output.replace(output[begin:(end+6)], "")

        if name == 'Blink':
            print(output)

        path = "output/" + name.replace(" ", "_").replace("/", "_").lower() + '.tex'
        with open(path, "w") as file:
            file.write(output)

if __name__ == '__main__':
    main()
