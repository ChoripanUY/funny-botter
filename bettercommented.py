# Importing necessary libraries
import requests, os, discord, random, json, asyncpraw
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the filenames
rps_filename = "rps.json"
economy_filename = "economy.json"

# Create the rock paper scissors data file if it doesn't exist
if not os.path.exists(rps_filename):
    with open(rps_filename, "w") as f:
        json.dump({}, f)

# Create the economy data file if it doesn't exist
if not os.path.exists(economy_filename):
    with open(economy_filename, "w") as f:
        json.dump({}, f)

# Function to load rock paper scissors game data from file
def load_data():
    with open(rps_filename, "r") as f:
        return json.load(f)

# Function to save rock paper scissors game data to file
def save_data(data):
    with open(rps_filename, "w") as f:
        json.dump(data, f, indent=4)

def load_economy():
    with open(economy_filename, "r") as f:
        return json.load(f)

def save_economy(data):
    with open(economy_filename, "w") as f:
        json.dump(data, f, indent=4)

# Create Discord bot instance with all intents and set command prefix
bot = commands.Bot(command_prefix="Mr!", intents=discord.Intents.all())

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} is on")
    await bot.tree.sync()  # Sync slash commands

    # Initialize Reddit API client
    global myReddit
    myReddit = asyncpraw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT")
    )
# Event handler to close the Reddit requestor
@bot.event
async def on_close():
    await myReddit.close()

# Error handling for various command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("That command does not exist")
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("You do not have permissions to use this command")
    elif isinstance(error, commands.errors.MemberNotFound):
        await ctx.send("That member does not exist")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds")

# Command to insult a user
@commands.cooldown(1, 3, commands.BucketType.guild)
@discord.app_commands.describe(user="The user you want to insult")
async def quote(ctx, user: discord.User):
    # Fetch a random insult from the API
    response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json").json()

    # Determine the correct user mention based on the interaction type
    correct_form = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author

    # Check if the bot is being insulted and respond accordingly
    if user == bot.user:
        message = f"Shush {correct_form.mention}"
    else:
        message = f"{response['insult']} {user.mention}"

    await ctx.send(message)

# Command to get a random number fact
@commands.cooldown(1, 3, commands.BucketType.guild)
@bot.hybrid_command(name="number", description="Say a random fact about a random number")
async def num(ctx):
    # Choose a random number fact category and fetch the fact from the API
    url = requests.get("http://numbersapi.com/random/" + random.choice(["math?json", "trivia?json", "year?json"]))
    response = url.json()

    await ctx.send(response["text"])

# Command to get a random Chuck Norris fact
@commands.cooldown(1, 3, commands.BucketType.guild)
@bot.hybrid_command(name="chuck_norris", description="Say a random fact about Chuck Norris 👀")
async def chuck_norris(ctx):
    response = requests.get("https://api.chucknorris.io/jokes/random").json()

    await ctx.send(response["value"])

# Command to get a random dad joke
@commands.cooldown(1, 3, commands.BucketType.guild)
@bot.hybrid_command(name="dad_joke", description="Say a random dad joke. You will die")
async def dad(ctx):
    url = "https://icanhazdadjoke.com/"
    headers = {
        "Accept" : "application/json"
    }
    response = requests.get(url, headers=headers).json()

    await ctx.send(response["joke"])

# Command to answer yes or no to a question
@commands.cooldown(1, 3, commands.BucketType.guild)
@bot.hybrid_command(name="yes_or_no", description="The bot will answer yes or no")
@discord.app_commands.describe(question="The question you want to ask the bot. The answer will be either yes or no")
async def yesno(ctx, *, question: str):
    # Fetch a yes/no response with an image
    response = requests.get("https://yesno.wtf/api").json()

    message = f"The question was: **{question}** to which I respond:"

    # Handle different response types for interactions and regular commands
    if isinstance(ctx, discord.Interaction):
        await ctx.response.send_message(message)
        await ctx.followup.send(response["image"])
    else:
        await ctx.send(message)
        await ctx.send(response["image"])

# Command to get a random meme from Reddit
@commands.cooldown(1, 3, commands.BucketType.guild)
@bot.hybrid_command(name="random_meme", description="Get a random meme from Reddit")
async def rand_meme(ctx):
    mySubreddits = ["memes", "dankmemes", "blursedimages", "funny", "TikTokCringe", "BlackPeopleTwitter", "me_irl", "193"]

    subreddit = await myReddit.subreddit(random.choice(mySubreddits))
    submissions = []
    async for submission in subreddit.hot(limit=100):
        submissions.append(submission)

    valid_extensions = (".gif", ".gifv", ".jpeg", ".jpg", ".png")
    valid_submissions = [sub for sub in submissions if sub.url.lower().endswith(valid_extensions)]

    random_submission = random.choice(valid_submissions)
    embed = discord.Embed(
        title=random_submission.title,
        colour=discord.Colour.from_rgb(115, 215, 255)
    )
    embed.set_image(url=random_submission.url)

    await ctx.send(embed=embed)

# Command to display information about the bot's commands
@commands.cooldown(1, 3, commands.BucketType.guild)
@bot.hybrid_command(name="bot_help", description="Get a list of all available commands")
async def help_command(ctx):
    # Create the embed with command information
    embed = discord.Embed(
        title="Commands:",
        colour=discord.Colour.from_rgb(174, 214, 241)
    )
    # Add fields for each command
    embed.add_field(name= "/insult", value="Insult someone")
    embed.add_field(name= "/number", value="Make the bot say a random fact about a random number")
    embed.add_field(name= "/chuck_norris", value="Make the bot say a random fact about Chuck Norris")
    embed.add_field(name= "/dad_joke", value="Make the bot say a dad joke")
    embed.add_field(name= "/yes_or_no", value="Ask the bot a question. The bot will answer either yes or no")
    embed.add_field(name= "/help", value="Get a list of all available commands")
    embed.add_field(name= "/rock_paper_scissors", value="Play rock paper scissors with the bot")
    embed.add_field(name= "/random_meme", value="Get a random meme from Reddit")
    
    await ctx.send(embed=embed)

# Command to play rock paper scissors with the bot
@commands.cooldown(1, 3, commands.BucketType.guild)
@bot.hybrid_command(name="rock_paper_scissors", description="Play rock paper scissors with the bot")
@discord.app_commands.describe(choice="Choose between rock, paper or scissors")
@discord.app_commands.choices(choice=[
    discord.app_commands.Choice(name="Rock", value="rock"),
    discord.app_commands.Choice(name="Paper", value="paper"),
    discord.app_commands.Choice(name="Scissors", value="scissors")
])
async def rock_paper_scissors(ctx, choice: str):
    # Bot makes a random choice
    bot_choice = random.choice(["rock", "paper", "scissors"])
    user_choice = choice.lower()
    
    # Load existing game data
    data = load_data()

    user_id = str(ctx.author.id)

    # Create user data if it doesn't exist
    if user_id not in data:
        data[user_id] = {"wins": 0, "losses": 0}

    # Determine the winner and update scores
    if (user_choice == "rock" and bot_choice == "scissors") or \
   (user_choice == "paper" and bot_choice == "rock") or \
   (user_choice == "scissors" and bot_choice == "paper"):
        result = f"You win! You chose {user_choice}, and I chose {bot_choice}."
        data[user_id]["wins"] += 1
    else:
        result = f"I win! You chose {user_choice}, and I chose {bot_choice}."
        data[user_id]["losses"] += 1

    # Save updated game data
    save_data(data)

    # Send the result and current score
    await ctx.send(f"{result} Your current score: Wins: {data[user_id]['wins']}, Losses: {data[user_id]['losses']}")
    
@commands.cooldown(1, 900, commands.BucketType.user)
@bot.hybrid_command(name="work", description="Work for me!")
async def work(ctx):
    user_id = str(ctx.author.id)
    data = load_economy()

    phrases = [
    f"{ctx.author.mention} has worked as a cashier and earned",
    f"{ctx.author.mention} delivered pizzas and made",
    f"{ctx.author.mention} mowed lawns in the neighborhood and collected",
    f"{ctx.author.mention} walked dogs for busy pet owners and received",
    f"{ctx.author.mention} worked a shift at the local factory and earned",
    f"{ctx.author.mention} sold handmade crafts online and pocketed",
    f"{ctx.author.mention} did some freelance writing and got paid",
    f"{ctx.author.mention} helped out at a car wash and made",
    f"{ctx.author.mention} worked as a street performer and collected",
    f"{ctx.author.mention} completed online surveys and earned",
    f"{ctx.author.mention} worked overtime at the office and received",
    f"{ctx.author.mention} offered tech support and was paid",
    f"{ctx.author.mention} taught an online class and made",
    f"{ctx.author.mention} worked as a virtual assistant and earned",
    f"{ctx.author.mention} did some gardening work and collected"
    ]


    if not user_id in data:
        data[user_id] = {"money": 0}
    
    randphrase = random.choice(phrases)
    added_money = random.randint(120, 450)
    data[user_id]["money"] += added_money

    embed = discord.Embed(
        title="You worked!",
        description=f"{randphrase} ${added_money} **Skibidi Coins**",
        colour=discord.Colour.dark_green()
    )
    save_economy(data)
    await ctx.send(embed=embed)

@commands.cooldown(1, 1200, commands.BucketType.user)
@bot.hybrid_command(name="crime", description="Commit a crime for money!")
async def crime(ctx):
    user_id = str(ctx.author.id)
    data = load_economy()

    success_phrases = [
    f"{ctx.author.mention} pulled off a daring heist and got away with",
    f"{ctx.author.mention} hacked into a digital vault and transferred",
    f"{ctx.author.mention} organized a complex scheme and pocketed",
    f"{ctx.author.mention} snuck into a high-security area and snagged",
    f"{ctx.author.mention} conducted a risky operation and secured",
    f"{ctx.author.mention} executed a cunning plan and acquired",
    f"{ctx.author.mention} orchestrated a clever con and walked away with",
    f"{ctx.author.mention} infiltrated a secret facility and escaped with",
    f"{ctx.author.mention} cracked a supposedly unbreakable safe and obtained",
    f"{ctx.author.mention} conducted some shady business and earned",
    f"{ctx.author.mention} engaged in some questionable activities and gained",
    f"{ctx.author.mention} took a walk on the wild side and came back with",
    f"{ctx.author.mention} bent the rules of society and profited",
    f"{ctx.author.mention} lived dangerously for a day and collected",
    f"{ctx.author.mention} took a big risk and it paid off with"
    ]

    caught_phrases = [
    f"{ctx.author.mention} got caught red-handed and had to pay a fine of",
    f"{ctx.author.mention}'s plan backfired, resulting in a penalty of",
    f"{ctx.author.mention} tripped the alarm and lost",
    f"{ctx.author.mention}'s scheme unraveled, costing them",
    f"{ctx.author.mention} was outsmarted by security and fined",
    f"{ctx.author.mention}'s luck ran out, and they had to forfeit",
    f"{ctx.author.mention} got busted and had to cough up",
    f"{ctx.author.mention}'s criminal career hit a snag, losing them",
    f"{ctx.author.mention} faced the consequences and paid",
    f"{ctx.author.mention}'s risky venture failed, costing them",
    f"{ctx.author.mention} couldn't talk their way out and lost",
    f"{ctx.author.mention}'s master plan fell apart, resulting in a loss of",
    f"{ctx.author.mention} got a taste of justice and had to pay",
    f"{ctx.author.mention}'s crime spree came to an abrupt end, costing",
    f"{ctx.author.mention} learned crime doesn't pay and lost"
    ]

    if not user_id in data:
        data[user_id] = {"money": 0}

    if random.randint(1, 100) <= 65:
        amount = random.randint(120, 450) * 3
        data[user_id]["money"] += amount
        phrase = random.choice(success_phrases)
        colour = discord.Colour.brand_red()
    else:
        amount = random.randint(120, 450) * 4
        data[user_id]["money"] -= amount
        phrase = random.choice(caught_phrases)
        colour = discord.Colour.dark_red()
    
    embed = discord.Embed(
        title="You committed a crime!",
        description=f"{phrase} ${amount} **Skibidi Coins**",
        colour=colour
    )
    save_economy(data)
    await ctx.send(embed=embed)

@commands.cooldown(1, 60, commands.BucketType.user)
@bot.hybrid_command(name="balance", description="Check your balance!")
async def balance(ctx):
    user_id = str(ctx.author.id)
    data = load_economy()

    if not user_id in data:
        data[user_id] = {"money": 0}

    embed = discord.Embed(
        title="Your balance",
        description=f"You have ${data[user_id]['money']} **Skibidi Coins**",
        colour=discord.Colour.dark_green()
    )
    await ctx.send(embed=embed)

@commands.cooldown(1, 300, commands.BucketType.user)
@bot.hybrid_command(name="gamble", description="Gamble your $Skibidi Coins!")
@discord.app_commands.describe(
    choice="Choose between Skibidi Toilet or Titan Speakerman",
    amount="The amount of Skibidi Coins you want to gamble"
)
@discord.app_commands.choices(choice=[
    discord.app_commands.Choice(name="Skibidi Toilet", value=1),
    discord.app_commands.Choice(name="Titan Speakerman", value=2)
])
async def gamble(ctx, choice: discord.app_commands.Choice[int], amount: int):
    user_id = str(ctx.author.id)
    data = load_economy()

    if user_id not in data:
        data[user_id] = {"money": 0}

    if data[user_id]["money"] == 0 or amount > data[user_id]["money"]:
        await ctx.send("You do not have enough money to gamble!")
        return
    
    if amount < 30:
        await ctx.send("The minimum amount of money you need to gamble is 30!")
        return
    
    result = random.randint(1, 2)

    if choice.value == result:
        await ctx.send(f"You win! You get ${amount * 2} Skibidi Coins")
        data[user_id]["money"] += amount * 2
    else:
        await ctx.send(f"You lost and the house takes ur ${amount} Skibidi Coins")
        data[user_id]["money"] -= amount

    save_economy(data)  # Don't forget to save the updated economy data

    
# Run the bot using the API key from the .env file
bot.run(os.getenv("API_KEY"))