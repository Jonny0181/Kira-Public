<p align="center">
  <a href="https://github.com/JonnyBoy2000/Kira-Miki">
    <img src="kira_banner.png"width="1000" height="200">
  </a>
  <p align="center">
    A multi purpose Discord bot. Made by Jonny™ with ❤!
    <br/>
    <a href="https://discord.gg/dbUFDg7">Discord Support</a>
    |
    <a href="https://discordapp.com/oauth2/authorize?client_id=538344287843123205&scope=bot&permissions=267779137">Public Invite Link</a>
  </p>
</p>

## Table of Contents
* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
  * [Developer?](#developer)
  * [Not a Developer?](#not-a-developer-but-still-want-to-help-out)
* [License](#license)
* [Contact](#contact)

## About The Project
Kira Miki is a discord bot I have created out of boredom. I have used a lot of old code I've had in the past. But I have re-worked most of the code to work the way I want it to now. Kira has multiple different features. Varying from moderation, music, utility, to fun commands. I'm probably going to be working on this project for quite some time. So I guess whoever is following this and has an instance of thier own is going to get a little annoyed with how many updates I make. :smile: Keep in mind tho, some code you may notice you have maybe seen somewhere before. You may be correct, and you may not be. Some of the code I use in the bot was not technically made by me. I have ajusted some code to work the way I need it to. But I fully do not claim ***all*** of the code as mine.

### Built With
Here you will find some things you will need.
* [Lavalink.py](https://github.com/JonnyBoy2000/Lavalink.py)
* [Lavlink.jar](https://github.com/Frederikam/Lavalink)
* [Discord.py Rewrite](https://github.com/Rapptz/discord.py/)
* [Python3.6+](https://www.python.org/)
* [MongoDb](https://docs.mongodb.com/)
* [Java Oracle](https://www.oracle.com/java/)

## Getting Started
Read to install and setup? No problem! That's what this part of the page is for.

### Installation
1) Install python if you don't have it already. (Make sure to install version 3.6 or later)
2) Install java also if you don't have it
3) Install and setup mongodb you can do so here.
```
Windows: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/
Linux: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
Others: There is a list at the top of the page. (https://docs.mongodb.com/manual/tutorial/)
```
4) You're going to need a Spotify api key for the music module.
```
You should be able to get one here. https://developer.spotify.com/web-api/
```
5) Clone the repo
```sh
git clone https://github.com/JonnyBoy2000/Kira-Public
```
6) Move into the bots directory
```sh
cd Kira-Public
```
7) Install requirements
```sh
sudo python3.6 -m pip install -r requirements.txt
```
8) Rename `config_exmaple.yml` to `config.yml` and set prefix as the prefix you want, and token as your bots token.
```sh
mv config_exmaple.yml config.yml
```
9) Run this command to download the Lavalink.jar file.
```sh
cd Lavalink && wget https://github.com/Frederikam/Lavalink/releases/download/3.2.0.3/Lavalink.jar
```
10) Start a screen session, press enter, and type the following command to startup the Lavalink server for music.
```sh
screen
(press enter)
sudo java -jar Lavalink.jar
```
11) Disconnect from the screen session by pressing ctrl+A+D
12) Now you should be able to run the bot! Just type the following command! 
```sh
cd .. && python3.6 kira.py
```

## Usage
<p>
  Now how do I use the bot? Well it's simple, keep in mind that <b>[p]</b> = the prefix you set in your <b>config.yml</b>.
  <br/>
  Every command needs to started with your bots prefix. Like so <b>[p]play</b>, <b>[p]help</b>, <b>[p]ping</b>.
  <br/>
  To get all of the bots commands use the following <b>[p]help</b>.
  <br/>
  If you are wanting help on a specific module use the following <b>[p]help ModuleName</b>.
  <br/>
  Also if you're wanting help on a specific command use the following <b>[p]help CommandName</b>.
</p>

## Contributing
Want to help out an contribute? Keep in mind that any contributions you make are **greatly appreciated**.

### Developer?
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Not a developer but still want to help out?
<p>
  That's okay, you can head over to my patreon, or my paypal.
  <br/>
  Patreon: https://www.patreon.com/user?u=8692289
  <br/>
  PayPal: https://paypal.me/YoungBrooklyn?locale.x=en_US
</p>

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
<p>
  You can join the Discord support server at the top of this page.
  <br/>
  You can also email me at jonny.boyy0510@icloud.com
  <br/>
  I might give you more options to contact me, but now right now.
</p>
