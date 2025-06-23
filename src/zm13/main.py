import datetime

import typer

from zm13 import mathtools

app = typer.Typer()


@app.callback()
def callback():
    """
    A Collection of Useful Commands
    """


@app.command()
def now():
    """
    Show local date and time
    """
    today = datetime.datetime.today()
    typer.echo(today.strftime('%A, %B %d, %Y'))


@app.command()
def gcd(x: int, y: int):
    """
    Greatest Common Divisor
    """
    typer.echo(mathtools.gcd(x, y))


@app.command()
def lcm(x: int, y: int):
    """
    Least Common Multiple
    """
    typer.echo(mathtools.lcm(x,y))


@app.command()
def is_prime(x: int):
    """
    Prime Number
    """
    typer.echo(mathtools.is_prime(x))


@app.command()
def more_study(x: int):
    """
    Study
    """
    if 0<=x<3:
        print("何やってるんですか！勉強してください！")
    elif 3<=x<6:
        print("もっと燃えられるはずだ。明日も頑張ろう！")
    elif 6<=x<9:
        print("なかなかやるじゃないか！")
    elif 9<=x<13:
        print("すごいじゃないか！")
    elif 13<=x<15:
        print("趣味とかにも，励んだ方がいいぞ。")
    elif 15<=x<25:
        print("もう大丈夫だから，体を壊さないようにしてくれよ。")
    else :
        pass

@app.command()
def total_interest(m:int, r:float, n:int):
    """
    Compound Interest
    """
    typer.echo(m * (1 + r) ** n) 





