# Import the main library for interacting with Discord.
import discord

#  Import the library for generating dice rolls.
import random

# Import the library for dynamically searching through strings.
import re

# Import the library for handling the spell data.
import json

# Import the library for getting the current time.
from time import gmtime, strftime

# Import the data and configuration.
from data import *

# Import the private token.
from private import TOKEN

# Initialise the client/bot
client = discord.Client()

# =================================

# Just a few session attributes for stuff like tracking initiave.
HISTORY = []
INITIAVE = []

# =================================


def handle_dice(arguments):
    # Arguments come through like "d20" or "5d20"
    arguments = arguments.split("d")  # ["4", "20"]
    debug("Splitted arguments: {}".format(arguments))

    if arguments[0] == "":
        arguments[0] = "1"

    try:
        arguments = list(map(lambda x: int(x), arguments))
    except Exception as E:
        print(E)
        return create_error("Couldn't understand your dice", "I tried my hardest, but I couldn't understand what you meant with your dice thing. It was probably your fault.")

    if arguments[0] > 500:
        return create_error("Woah! Steady on...", "That's wayyy too many dice, and if you go much further, you'll probably break me, so hold on there.")

    elif arguments[0] == 1:
        result = random.randint(1, arguments[1])

        if result == 20 and arguments[1] == 20:
            phrases = ["It's a critical!", "It's a critical success!", "You got a critical!",
                       "It's a twenty!", "Oh boy! It's a critical!", "20!", "Wow, it's 20!"]

            embed = discord.Embed(
                title="d20 Die Roll",
                description="**{}**".format(random.choice(phrases)),
                color=0xce0000
            )

            embed.set_author(name='Dice Roller',
                             icon_url=client.user.default_avatar_url)

            return embed

        elif result == 1 and arguments[1] == 20:
            phrases = ["Aw man, it's a one.", "Eek. It's one.",
                       "It's a critical! (failure)", "It's a critical... failure.", "You got a one. Tough luck."]

            embed = discord.Embed(
                title="d20 Die Roll",
                description="*{}*".format(random.choice(phrases)),
                color=0xce0000
            )

            embed.set_author(name='Dice Roller',
                             icon_url=client.user.default_avatar_url)

            return embed

        else:
            phrases = ["Sure, it was {}.",
                       "Ok, it was {}.", "It's {}.", "You got {}."]

            embed = discord.Embed(
                title="d{} Die Roll".format(arguments[1]),
                description=(random.choice(phrases)).format(result),
                color=0xce0000
            )

            embed.set_author(name='Dice Roller',
                             icon_url=client.user.default_avatar_url)

            return embed

    else:
        results = []

        for i in range(arguments[0]):
            results.append(random.randint(1, arguments[1]))

        result_string = ", ".join(
            list(map(lambda x: str(x), results[:-1]))) + " and " + str(results[-1])

        phrases = ["Sure, they're {}.", "{}.", "Okey dokey, {}.",
                   "Why, sure: {}.", "Here you go: {}."]

        result_sum = sum(results)
        result_min = min(results)
        result_max = max(results)

        result_mean = result_sum/len(results)

        embed = discord.Embed(
            title="{}d{} Dice Roll".format(arguments[0], arguments[1]),
            description="{}\n\n".format(
                (random.choice(phrases)).format(result_string)),
            color=0xce0000
        )

        embed.add_field(
            name="Sum:", value="{}".format(result_sum), inline=False)
        embed.add_field(name="Min, Max:", value="Min is {} and max is {}.".format(
            result_min, result_max), inline=False)
        embed.add_field(
            name="Mean:", value="{}".format(round(result_mean * 100) / 100), inline=False)

        embed.set_author(name='Dice Roller',
                         icon_url=client.user.default_avatar_url)

        return embed


def get_spell(arguments):
    data = {}

    with open("data.json", "r") as f:
        data = json.loads(f.read())["data"]

    names = []

    for spell in data:
        names.append(spell["name"])

    if arguments == []:
        # No spell in particular, wants them ALL!
        debug("User wants all spells. This can't be done because the message length is over 2000.")

        return create_error("Sorry, no can do.", "I guess you want a list of all the avaliable spells. This can't be done because there's just too many. You can search for an individual spell by doing:\n`/dnd spell <spell name>`.")

    arguments = list(map(lambda x: x.lower(), arguments))

    requested_spell_name = " ".join(arguments)

    possible = []
    real = []

    for i in range(len(names)):
        name = names[i]

        if re.search("^" + requested_spell_name, name.lower()):
            possible.append([name, i])

    if len(possible) > 1:
        embed = discord.Embed(
            title="Error:",
            description="Unfortunately, more than one spell has a name like that. My greatest apologies.",
            color=0xce0000
        )

        other_spells = ""

        for spell in possible:
            other_spells += "\n- {}".format(spell[0])

        embed.add_field(name="Did you mean...", value=other_spells)

        embed.set_author(name='Spell Lookup',
                         icon_url=client.user.default_avatar_url)

        return embed

    elif len(possible) == 0:
        return create_error("Oops. I don't know that one.", "I'm sorry, the list of all the spells is still being built on, and there is many that I don't understand yet.")

    else:
        real = possible[0]

    spell_data = data[real[1]]
    name = spell_data["name"]

    embed = discord.Embed(
        title=name,
        description="\n\n".join(spell_data["desc"]) + "\n\n",
        color=0xce0000
    )

    embed.set_author(name='Spell Lookup',
                     icon_url=client.user.default_avatar_url)

    embed.add_field(name="Level", value="{} is a level {} {} spell.".format(
        name, spell_data["level"], spell_data["school"]["name"]) + "\n\n", inline=False)

    try:
        embed.add_field(name="At Higher Levels",
                        value="\n".join(spell_data["higher_level"]) + "\n\n", inline=False)
    except Exception as e:
        embed.add_field(name="At Higher Levels",
                        value="*No information given.*" + "\n\n", inline=False)

    embed.add_field(name="Components", value="The components are {}".format(
        ", ".join(spell_data["components"])) + "\n\n", inline=False)

    try:
        embed.add_field(name="Materials",
                        value=spell_data["material"] + "\n\n", inline=False)

    except Exception as e:
        pass

    embed.add_field(name="Other", value="""
    - Range: {}
    - Duration: {}
    - Casting Time: {}
    - Concentration: {}
    - Ritual: {}
    """.format(spell_data["range"], spell_data["duration"], spell_data["casting_time"], spell_data["concentration"], spell_data["ritual"], ), inline=False)

    return embed


def help(command="*"):
    if command == "*":
        embed = discord.Embed(
            title="Commands:",
            description="These are the commands you can use to interact with the bot.\n\n",
            color=0xce0000
        )

        embed.set_author(name='Help',
                         icon_url=client.user.default_avatar_url)

        embed.add_field(name="Dice Rolling/Generation", value="You can roll dice in one of two ways using this discord bot.\n\nFirstly, you can do it quickly by just typing `/d20` or `/8d12`. However, this only works up to a max of `99` dice at once.\nAlternatively, you can do `/dnd roll d20` or `/dnd roll 8d12`. This has support all the way up to a max of `500`.\n\n\n")

        embed.add_field(name="Spell Lookups/Information", value="You can also easily look up spells using the bot.\n\n`/dnd spell <spell name>` or `/dnd s <spell name>` will return the information about the spell specified.\nOne thing to keep in mind whilst doing this is that the spell only has to be a substring of the spell name.\nFor example, `/dnd spell acid sp` will still return information about the 'acid splash' spell as it is the closest match. Conversly, `/dnd spell A` will return all the spells that start with an 'A'.\n\n\n")

        embed.add_field(name="Help", value="As well as displaying this with all the information on it, you can also get information on specific commands.\n\nFor example, /dnd help roll will return help on just dice rolling.")

        return embed

    elif command == "roll":
        embed = discord.Embed(
            title="Dice Rolling:",
            description="There are two ways you can roll dice using this Discord bot. The first is the shorthand method and the second is the long way.",
            color=0xce0000
        )

        embed.add_field(name="Dice Shorthand", value="`/d20` or `/8d12` is the format of the dice rolling shorthand.\nIn general the format is `/<amount of dice>d<die type>` or for just one single roll, `/d<die type>`.\nHowever, it should be noted that the limit to the amount of dice this can do at once is capped at **99**, but you can go up to *500* using the longhand method.\n\n\n")

        embed.add_field(name="Dice Longhand", value="`/dnd roll d20` or `/dnd roll 8d12` is the format of dice rolling in general. It produces the same results as the shorthand method, except the amount of dice it can roll at once is capped at **500** instead of *99*.\n\n\n")

        embed.set_author(name='Help',
                         icon_url=client.user.default_avatar_url)

        return embed

    elif command == "spell":
        embed = discord.Embed(
            title="Looking up Spells:",
            description="You can look up spells using this Discord bot. There's only one way to perform the command.",
            color=0xce0000
        )

        embed.add_field(name="Command", value="You can find details about a DND spell by using the following command:\n\n`/dnd spell <spell name>`\n\nThis will search the DND SRD (DND spell description database) and find all the info it can.\n\nFor example `/dnd spell Zone of Truth` will find the info on the spell 'Zone of Truth' and place the information in the chat.\n\nIt should be noted, however, that you can perform this quickly by just typing the start or some substring inside the spell. For example:\n\n`/dnd spell zone`\n\nwould produce the same result.")

        return embed


def create_error(error_title, error_description):
    embed = discord.Embed(
        title=error_title,
        description=error_description,
        color=0xce0000
    )

    embed.set_author(name='Error',
                     icon_url=client.user.default_avatar_url)

    return embed


def is_for_bot(message):
    # Checks if the message sent was actually for the discord bot.
    if message.author == client.user:
        debug("Message was from the bot, so no computation is needed.")
        return False

    # Checks if the bot is either of the form "/dnd" or "/d4" or /4d4
    elif (not message.content.startswith("/dnd")) and (not message.content.split(" ")[0][1:] in STRING_DIE_TYPES) and (not message.content.split(" ")[0][2:] in STRING_DIE_TYPES) and (not message.content.split(" ")[0][3:] in STRING_DIE_TYPES):
        debug("Message wasn't an invocation of the bot, so no computation is needed.")
        return False

    else:
        debug("Message was for bot, allowing code to proceed.")
        return True


def parse_message(message):
    # Parses a message into an array that can be easily used to understand commands.
    debug("Parsing message...")
    text = message.content

    try:
        # The message is of the form "/d20".
        if text.split(" ")[0][1:] in STRING_DIE_TYPES:
            debug("Message was of the form {}, so a single short hand die.".format(text))
            text = text[1:]  # This turns something like "/d20" into "d20"

            debug("Returning: {}".format(["success", ["roll", text]]))
            return ["success", ["roll", text]]

        # Message is of the form "/4d20" or similar.
        elif text.split(" ")[0][2:] in STRING_DIE_TYPES:
            debug(
                "Message was of the form {}, so a multiple short hand dice.".format(text))
            text = text[1:]  # This turns something like "/4d20" into "4d20"

            debug("Returning: {}".format(["success", ["roll", text]]))
            return ["success", ["roll", text]]

        elif text.split(" ")[0][3:] in STRING_DIE_TYPES:
            debug(
                "Message was of the form {}, so a multiple short hand dice.".format(text))
            text = text[1:]  # This turns something like "/4d20" into "4d20"

            debug("Returning: {}".format(["success", ["roll", text]]))
            return ["success", ["roll", text]]

        elif text == "/dnd":
            debug("User just put /dnd.")
            return ["success", ["help"]]

        else:

            debug("Returning: {}".format(["success", text.split(" ")[1:]]))
            return ["success", text.split(" ")[1:]]

    except:
        return ["error", create_error("Couldn't understand your message", "I'm really sorry, I couldn't understand your message.")]

# =================================

# Handles what happens when a message comes through.


@client.event
async def on_message(message):
    debug("Message Incoming: {}".format(message.content[:20] + "..."))

    if not is_for_bot(message):  # Checks if message was for bot.
        return

    log("Message recieved for bot: '{}', from user '{}'.".format(
        message.content, message.author))

    parsed = parse_message(message)
    debug("Parsed message recieved was: {}".format(parsed))

    if parsed[0] == "error":
        # There was an error parsing, so return an error.
        debug("There was an error while parsing the message.")
        await client.send_message(message.channel, embed=parsed[1])

    else:
        command = parsed[1][0]
        arguments = parsed[1][1:]

        debug("Command is '{}'".format(command))
        debug("Arguments are '{}'".format(arguments))

        if command == "roll" or command == "r":
            await client.send_message(message.channel, embed=handle_dice(arguments[0]))

        elif command == "spell" or command == "spells" or command == "s":
            await client.send_message(message.channel, embed=get_spell(arguments))

        elif command == "help" or command == "h" or command == "":
            if arguments == []:
                await client.send_message(message.channel, embed=help())

            else:
                await client.send_message(message.channel, embed=help(arguments[0]))

        else:
            await client.send_message(message.channel, embed=create_error(
                "Invalid Command", "I don't really understand what you mean. If I should then I'm sorry, but if you're tricking me [bots have rights](https://reddit.com/r/botsrights)."))


# Handles what happens when the bot is switched on at the start.
@client.event
async def on_ready():
    # Get the current time.
    CURRENT_TIME = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    # Print a "header" so it's really clear where the log is.
    print("====== DND BOT STARTED ======")

    log("The Bot is logged in as \"{}\" (user id '{}').\n".format(
        client.user.name, client.user.id)
        )  # If logging is enabled, log the USERNAME of the bot and the USER ID.

    print("=============================")  # Another line for clarity.

    # Print the current time help with looking back through the logs.
    log("Logging start: {}".format(CURRENT_TIME))

if __name__ == "__main__":
    client.run(TOKEN)
