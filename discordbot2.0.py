import discord
from discord.ext import commands
import sqlite3, json
from bs4 import BeautifulSoup
import requests
import random,time,datetime,os




client= commands.Bot(command_prefix="!")

conn=sqlite3.connect('user_info.db')
cursor=conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS info (level integer, nickname text, id integer)""")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('...'))
    cursor.execute("SELECT id,level FROM info")
    global levels
    levels={}
    for user in cursor.fetchall():
        levels[user[0]]=user[1]
    print("Done")


@client.event
async def on_member_update(before,after):
    User_id = after.id
    cursor.execute("SELECT nickname FROM info WHERE id=?", [(User_id)])
    nick = cursor.fetchone()
    if after.display_name==nick[0]:
        pass
    else:
        await after.edit(nick=nick[0])

@client.event
async def on_member_join(member):
    channel = client.get_channel(690908836391026728)
    role = discord.utils.get(member.guild.roles, id=681396936011808791)
    await member.add_roles(role)
    await channel.send(f'{member.mention} залетел в бомжатник')
    sql="""INSERT INTO info VALUES (?,?,?)"""
    user_info=(1,f'{member.display_name}',f'{member.id}')
    cursor.execute(sql,user_info)
    conn.commit()
    levels[member.id]=1


# -------COMANDS-------



@client.command()
async def show(ctx):
    cursor.execute("SELECT * FROM info")
    all=cursor.fetchall()
    await ctx.send(all)
@client.command()
async def auth(ctx):
    if ctx.author.id!=229033111197843456:
        pass
    else:
        member_list=[]
        for member in ctx.author.guild.members:
            member_list.append((3,member.display_name,member.id))
        cursor.executemany("""INSERT INTO info VALUES(?,?,?)""",member_list)
        conn.commit()

@client.command()
async def level(ctx,member:discord.Member=None):
    member=member or ctx.author
    cursor.execute("SELECT level FROM info WHERE id=?",[(member.id)])
    lvl=cursor.fetchone()
    await ctx.send(f"У {member.mention} {lvl[0]} уровень")


@client.command()
async def lvlup(ctx, member:discord.Member, level):
    if ctx.author.id!=229033111197843456:
        ctx.send('Писька не выросла')
        try:
            ctx.author.move_to(None)
        except:
            pass
    else:
        sql="""UPDATE info SET level={0} WHERE id={1}""".format(level,member.id)
        cursor.execute(sql)
        conn.commit()
        levels[member.id]=level
        await ctx.send(f'Уровень {member.mention} был повышен до {level}')

@client.command()
async def changenick(ctx,member:discord.Member,nick):
    if levels[ctx.author.id]<5:
        await ctx.send("Хуй тебе")
    else:
        sql="""UPDATE info SET nickname=? WHERE id=?"""
        params=(str(nick),member.id)
        cursor.execute(sql,params)
        conn.commit()
        await member.edit(nick=nick)

@client.command()
async def nahui(ctx,member:discord.Member,duration=5):
    if levels[ctx.author.id]<4:
        await ctx.send('Хуй тебе')
    else:
        await member.move_to(None)
        def check(new_member,before,after):
            return new_member==member and before.channel is None and after.channel is not None
        start_time=datetime.datetime.now()
        start_time=start_time.second+start_time.minute*60+start_time.hour*3600
        end_time=start_time+duration
        while start_time<end_time:
            await client.wait_for('voice_state_update',check=check,timeout=duration)
            msg=await ctx.channel.history().get(author__name=ctx.author.name)
            if msg.content=="!stop":
                await ctx.channel.purge(limit=1)
                break
            else:
                now=datetime.datetime.now()
                now=now.second+now.minute*60+now.hour*3600
                if now<end_time:
                    await member.move_to(None)
                else:
                    break
@client.command()
async def stop(ctx):
    pass

@client.command()
async def clear(ctx,amount=2):
    await ctx.channel.purge(limit=amount)
    channel=client.get_channel(681414780351021090)
    await channel.send(f'{ctx.author.name} Очистил {amount} сообщений')

@client.command()
async def spam(ctx,member:discord.Member,amount=5,*,message='Тук-Тук'):
    if amount>200:
        pass
    else:
        if levels[ctx.author.id]<4:
            await ctx.send("Хуй тебе")
        else:
            for i in range(amount):
                await member.send(str(message))
                time.sleep(0.1)


@client.command()
async def petuh(ctx, member: discord.Member):
    if levels[ctx.author.id]>=5:
        with open('data_file.json','r') as file:
            TakenRoles=json.load(file)
        roles_to_take=[role.name for role in member.roles]
        TakenRoles[member.name]=roles_to_take
        with open('data_file.json','w') as file:
            json.dump(TakenRoles,file)
        mute_role = discord.utils.get(ctx.message.guild.roles, name='петушарня')
        await member.add_roles(mute_role)
        for i in range(len(roles_to_take)-1):
            await member.remove_roles(discord.utils.get(ctx.message.guild.roles, name=roles_to_take[i+1]))
        await member.move_to(client.get_channel(681777814995075075))
        await ctx.send(f'{member.mention} был лишен всех прав и отправлен в ПЕТУШАРНЮ')
    else:
        await ctx.send('Хуй тебе')

@client.command()
@commands.has_permissions(administrator=True)
async def unpetuh(ctx,member:discord.Member):
    with open('data_file.json', 'r') as file:
        TakenRoles = json.load(file)
    remove_role=discord.utils.get(ctx.message.guild.roles, name='петушарня')
    await member.remove_roles(remove_role)
    roles_to_give=TakenRoles[member.name]
    for role in range(len(roles_to_give)-1):
        await member.add_roles(discord.utils.get(ctx.message.guild.roles, name=roles_to_give[role+1]))
    await ctx.send(f'{ctx.author.mention} вытащил {member.mention} из ПЕТУШАТНИ и вернул все права')


@client.command()
async def kick(ctx,member:discord.Member):
    if levels[ctx.author.id]<4:
        await ctx.send("Хуй тебе")
    else:
        if levels[member.id]>=5:
            await ctx.send('Неа, хуй там плавал')
        else:
            channel=client.get_channel(681414780351021090)
            await member.kick()
            await ctx.send(f'{ctx.author} выпнул бомжа {member.mention}')
            await channel.send(f'{ctx.author.mention} kicked {member.mention}')


@client.command()
async def ban(ctx,member:discord.Member,reason='За кривой базар'):
    if levels[ctx.author.id] < 5:
        await ctx.send("Хуй тебе")
    else:
        if levels[member.id] >= 5:
            await ctx.send('Неа, хуй там плавал')
        else:   
            channel = client.get_channel(681414780351021090)
            await member.ban(reason=reason)
            await ctx.send(f'{ctx.author.mention} закрыл доступ в петушатню {member.mention} {reason}')
            await channel.send(f'{ctx.author.mention} has banned {member.mention} for {reason}')


@client.command()
async def covid(ctx):
    def get_response():
        URL = "https://yandex.ru/search/?clid=2358536&text=число%20заболевших%20коронавирусом%20в%20россии&l10n=ru&lr=11393"
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36 OPR/67.0.3575.105'
        }
        response = requests.get(url=URL, headers=HEADERS)
        corona = BeautifulSoup(response.content, 'html.parser')
        covid_19 = corona.findAll('div', class_='sport-table__body-wrapper')
        covid = covid_19[0].find_all('div',
                                     class_='sport-table__row sport-table__row_gap_xl sport-table__row_border_yes')

        zhopa = {
            'infected': covid[0].contents[2].contents[0].contents[0],
            'healthy': covid[1].contents[2].contents[0].contents[0],
            'deaths': covid[2].contents[2].contents[0].contents[0]
        }
        return zhopa

    info = get_response()
    await ctx.send(
        f'Почти сдохли: {info["infected"]}\nУже сдохли: {info["deaths"]}\nЧудом спасшиеся: {info["healthy"]}')


@client.command()
async def bibametr(ctx, member: discord.Member = None):
    if ctx.author.id == 373686695490486272 and member == None or ctx.author.id == 373686695490486272 and member.id == 373686695490486272:
        await ctx.send(f'У {ctx.author.mention} нет бибы. Он лох')
    else:
        top_role = discord.utils.get(ctx.message.guild.roles, id=686468619533680650)
        member=member or ctx.author
        if top_role in member.roles:
            biba = random.randint(5, 25)
        else:
            biba = random.randint(1, 20)
        if biba < 5:
            await ctx.send(f'У {member.mention} биба {biba} см')
            biba_role = discord.utils.get(ctx.message.guild.roles, id=703583464653324328)
            await member.add_roles(biba_role)
            await ctx.send(f'{member.mention}Был отправлен к Короткостволам за маленькую бибу')
            for biba in range(random.randint(1, 10)):
                await member.send('.!. - твоя маленькая биба')
        elif biba < 10:
            await ctx.send(f'У {member.mention} маленькая биба {biba} см')
        elif biba < 15:
            await ctx.send(f'У {member.mention} биба внушительных размеров {biba} см')
        elif biba >= 19:
            await ctx.send(
                f'{member.mention} половой гигант, а его бибу можно заметить с космоса. Всё-таки целых {biba}см')


token=os.environ.get("BOT_TOKEN")
client.run(token)
