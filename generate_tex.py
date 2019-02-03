import json
import re
import sys

'''
To do:
- Work on area
- support tables in entries
- colors and other fonts? Bold dice and other important info in the text?
'''

vprint = print if "--debug" in sys.argv or "--verbose" in sys.argv else lambda *a, **k: None

def clean_text(text):
    text = text.replace('@condition ', '')
    text = text.replace('@dice ', '')
    text = text.replace('@creature ', '')
    text = text.replace('×', '$\\times$')
    text = text.replace('Ã', '$\\times$')   #Some weird encoding stuff where the x is actually this a
    text = text.replace('—', '')
    text = text.replace('\u22124', '-')
    text = text.replace('\u2212', '-')
    return text

def get_damage(spell, text):
    damage = spell['damageInflict'] if 'damageInflict' in spell else ["-"]
    dice = re.findall('\d+d\d+', text) + ["-"]
    if len(set(dice)) > 2:
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
        area = re.findall('\d+.foot.cone', text)[0]
        area = area.replace('.foot', 'ft')
    #sphere:
    elif 'sphere' in text and not "inch" in text:
        area = re.findall('\d+.[a-z]+.radius.{1,20}sphere', text)
        if len(area) > 0:
             area = area[0].replace('.foot', 'ft')
             area = area[:-7]
    #cube:
    elif 'cube' in text:
        area = re.findall('\d+.[a-z]+.cube', text)
        if len(area) > 0:
             area = area[0].replace('.foot', 'ft')
    #line:
    elif 'long line' in text or 'wide line' in text:
        area = re.findall('\d+.[a-z]+.wide, \d+.[a-z]+.long line', text)
        area += re.findall('\d+.[a-z]+.long, \d+.[a-z]+.wide line', text)
        if type(area) == list:
            if len(area) == 1:
                area = area[0]
            else:
                area = ", ".join(area)
        dim = re.findall('\d+.[a-z]+', area)
        area = dim[0] + " $\\times$ " + dim[1]
        area += " line"
        #area = area.replace('.foot', 'ft')
        #5-foot-wide, 60-foot-long line
    else:
        area = "-"
    if area == []:
        area = '-'
    return area

def format_text(entries):
    text = entries[0]        #This assumes the first entry is always plain text
    current = 1
    while current < len(entries):
        if type(entries[current]) == str:     #Plain text
            if type(entries[current]) == str:
                text += '\\\\\n'
            else:
                text += "\n\\bigskip\n"
            text += entries[current]
            text = clean_text(text)
        elif type(entries[current]) == dict and entries[current]['type'] == 'entries':    #E
            text += "\n\\bigskip\n"
            text += "\n\\begin{itemize}\n"
            while current < len(entries) and type(entries[current]) == dict and entries[current]['type'] == 'entries':
                text += "\\item "
                if "name" in entries[current]:
                    text += "\\textbf{" + entries[current]["name"] + ":} "
                text += entries[current]['entries'][0] + "\n"
                current += 1
            current -= 1
            text += "\\end{itemize}\n"
        elif type(entries[current]) == dict and entries[current]['type'] == 'list':
            text += "\n\\bigskip\n"
            text += "\n\\begin{itemize}\n"
            for item in entries[current]['items']:
                text += "\\item " + item + '\n'
            text += "\\end{itemize}\n"
            current += 1
        elif entries[current]['type'] == 'table':
            if type(entries[current]) == str:
                text += '\\\\\n'
            else:
                text += "\n\\bigskip\n"
            text += make_table(entries[current])
        current += 1
    return text

def convert_cell(cell):
    if type(cell) == str:
        return cell
    elif type(cell) == dict:
        if 'exact' in cell['roll']:
            return str(cell['roll']['exact'])
        else:
            return str(cell['roll']['min']) + ' to ' + str(cell['roll']['max'])
    else:
        print("I am confused by this table.")

def make_table(table):
    if 'caption' in table:
        caption = "\\textbf{\\large " + table['caption'] + "}\\\\"
    else:
        caption = ''
    begin_table = "\\begin{tabular}{l"
    row1 = table['colLabels'][0]
    for label in table['colLabels'][1:]:
        begin_table += "|l"
        row1 += ' & \\textbf{' + label + '}'
    begin_table += '}'
    row1 += '\\\\'
    rows = []
    for r in table['rows']:
        text = convert_cell(r[0])
        for entry in r[1:]:
            text += ' & ' + convert_cell(entry)
        text += '\\\\'
        rows.append('\\hline')
        rows.append(text)

    result = caption + '\n' + begin_table + '\n' +  row1 + '\n'
    for r in rows:
        result += r + '\n'
    result += '\\end{tabular}\n'
    return result

def convert(spell, template):
    name = spell['name']
    #if name not in ['Sunbeam']: return
    vprint(name)
    text = format_text(spell['entries'])

    if "entriesHigherLevel" in spell:
        higher = "\\\\\\phantom{-}\\\\" + "\n\\textbf{At Higher Levels: }" + spell['entriesHigherLevel'][0]['entries'][0]
        scale = re.findall('\{@scaledice .*\}', higher)
        if len(scale) > 0:
            higher = re.sub('\{@scaledice .*\}', scale[0][-4:-1], higher)
    else:
        higher = ""
    level = spell['level']
    if 'distance' in spell['range']:
        range = spell['range']['distance']['type']
        if 'amount' in spell['range']['distance']:
            range = str(spell['range']['distance']['amount']) + " " + range
    else:
        range = spell['range']['type']
    range = range.capitalize()
    components = ", ".join(list(zip(*list(spell['components'].items())))[0]).upper()
    save = spell['savingThrow'] if 'savingThrow' in spell else "-"
    if len(spell['duration']) > 1:
        print(name, "has multiple durations")
    time = str(spell['time'][0]['number']) + " " + spell['time'][0]['unit']
    duration = spell['duration'][0]['type']
    if duration == 'timed':
        duration = str(spell['duration'][0]['duration']['amount']) + " " + spell['duration'][0]['duration']['type']
    duration = duration.replace('instant', 'instantaneous').capitalize()
    #if 'amount' in spell['duration'][0]:
        #duration = str(spell['duration'][0]['amount']) + " " + duration
    if 'concentration' in spell['duration'][0] and spell['duration'][0]['concentration']:
        duration = "(C) " + duration
    if type(save) == list:
        save = ", ".join(save)
    save = save.capitalize()
    dice, damage = get_damage(spell, text)
    area = find_area(text)

    #higher = text[text.index("At Higher Levels:"):]
    output = template
    output = output.replace('<NAME>', name)    #this copies the template right?
    if level == 0:
        level = "Cantrip"
        output = output.replace('\\flushright\n    Level ', "\\flushright\n    ")
    output = output.replace('<LEVEL>', str(level))
    output = output.replace('<RANGE>', range)
    output = output.replace('<AREA>', area)
    output = output.replace('<COMPONENTS>', components)
    output = output.replace('<DURATION>', duration)
    output = output.replace('<TIME>', time)
    output = output.replace('<TEXT>', text)
    output = output.replace('<HIGHER>', higher)

    #clean up
    delete = 0
    if dice + " " + damage == "- -":
        output = output.replace("\\textbf{Damage}", " ")
        output = output.replace('<DAMAGE>', " ")
        delete += 1
        if save == "-":
            save = ""
            output = output.replace("\\textbf{Saving Throw}", " ")
            delete += 1
    else:
        output = output.replace('<DAMAGE>', dice + " " + damage)
    output = output.replace('<SAVE>', save)
    if area == "-":
        #output = output.replace("\\textbf{Area}", " ")
        delete += 1
    #remove empty table rows:
    if delete == 3:
        begin = output.index("%d_begin")
        end = output.index("%d_end")
        output = output.replace(output[begin:(end+6)], "")

    path = "output/" + name.replace(" ", "_").replace("/", "_").lower() + '.tex'
    with open(path, "w") as file:
        file.write(output)


def main():
    vprint("Loading data...")
    with open('template.tex', "r") as read_file:
        template = "".join(read_file.readlines())

    with open('data/spells-phb.json', "r") as read_file:
        data = json.load(read_file)
    with open('data/spells-scag.json', "r") as read_file:
        data['spell'] += json.load(read_file)['spell']
    with open('data/spells-xge.json', "r") as read_file:
        data['spell'] += json.load(read_file)['spell']
    #spells-phb.json seems to contain xge spells?
    vprint("Converting...")
    if '--debug' in sys.argv:
        for spell in data['spell']:
            convert(spell, template)
    else:
        for spell in data['spell']:#[40:42]:
            try:
                convert(spell, template)
            except (LookupError, TypeError, UnicodeEncodeError) as e:
                print("ERROR:", spell['name'], type(e))

if __name__ == '__main__':
    main()
