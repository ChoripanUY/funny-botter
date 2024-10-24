# Importing necessary libraries
import requests, os, discord, random, json, praw
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the filename for storing rock paper scissors game data
rps_filename = "rps.json"

# Create the rock paper scissors data file if it doesn't exist
if not os.path.exists(rps_filename):
    with open(rps_filename, "w") as f:
        json.dump({}, f)

# Initialize Reddit API client
myReddit = praw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT"),
)

# Function to load rock paper scissors game data from file
def load_data():
    with open(rps_filename, "r") as f:
        return json.load(f)

# Function to save rock paper scissors game data to file
def save_data(data):
    with open(rps_filename, "w") as f:
        json.dump(data, f, indent=4)

# Create Discord bot instance with all intents and set command prefix
bot = commands.Bot(command_prefix="Mr!", intents=discord.Intents.all())

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} is on")
    await bot.tree.sync()  # Sync slash commands

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
        await ctx.send(f"This command is on cooldown. Please try again later")

# Command to insult a user
@commands.cooldown(1, 5, commands.BucketType.user)
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
@commands.cooldown(1, 5, commands.BucketType.user)
@bot.hybrid_command(name="number", description="Say a random fact about a random number")
async def num(ctx):
    # Choose a random number fact category and fetch the fact from the API
    url = requests.get("http://numbersapi.com/random/" + random.choice(["math?json", "trivia?json", "year?json"]))
    response = url.json()

    await ctx.send(response["text"])

# Command to get a random Chuck Norris fact
@commands.cooldown(1, 5, commands.BucketType.user)
@bot.hybrid_command(name="chuck_norris", description="Say a random fact about Chuck Norris 👀")
async def chuck_norris(ctx):
    response = requests.get("https://api.chucknorris.io/jokes/random").json()

    await ctx.send(response["value"])

# Command to get a random dad joke
@commands.cooldown(1, 5, commands.BucketType.user)
@bot.hybrid_command(name="dad_joke", description="Say a random dad joke. You will die")
async def dad(ctx):
    url = "https://icanhazdadjoke.com/"
    headers = {
        "Accept" : "application/json"
    }
    response = requests.get(url, headers=headers).json()

    await ctx.send(response["joke"])

# Command to answer yes or no to a question
@commands.cooldown(1, 5, commands.BucketType.user)
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
@commands.cooldown(1, 5, commands.BucketType.user)
@bot.hybrid_command(name="random_meme", description="Get a random meme from Reddit")
async def rand_meme(ctx):
    # List of subreddits to choose from
    mySubreddits = ["memes", "dankmemes", "wholesomememes", "BlackPeopleTwitter", "me_irl", "195"]

    # Select a random subreddit and fetch hot submissions
    subreddit = myReddit.subreddit(random.choice(mySubreddits))
    submissions = list(subreddit.hot(limit=100))

    # Filter submissions to only include valid image formats
    valid_extensions = (".gif", ".gifv", ".jpeg", ".jpg", ".png")
    valid_submissions = [sub for sub in submissions if sub.url.lower().endswith(valid_extensions)]

    # Choose a random submission and create an embed
    random_submission = random.choice(valid_submissions)
    embed = discord.Embed(
        title=random_submission.title,
        colour=discord.Colour.from_rgb(115, 215, 255)
    )
    embed.set_image(url=random_submission.url)

    await ctx.send(embed=embed)

# Command to display information about the bot's commands
@commands.cooldown(1, 5, commands.BucketType.user)
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
@commands.cooldown(1, 5, commands.BucketType.user)
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
    
# Run the bot using the API key from the .env file
bot.run(os.getenv("API_KEY"))
