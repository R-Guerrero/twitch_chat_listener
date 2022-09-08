import subprocess

ASCII_HEADER = """
\t                                ______   __  __   ___     ______        
\t                               / ____/  / / / /  /   |   /_  __/        
\t         T  W  I  T  C  H     / /      / /_/ /  / /| |    / /           
\t                             / /___   / __  /  / ___ |   / /            
\t                             \____/  /_/ /_/  /_/  |_|  /_/             
\t    __       ____   _____   ______   ______   _   __   ______   ____  
\t   / /      /  _/  / ___/  /_  __/  / ____/  / | / /  / ____/  / __ \ 
\t  / /       / /    \__ \    / /    / __/    /  |/ /  / __/    / /_/ / 
\t / /___   _/ /    ___/ /   / /    / /___   / /|  /  / /___   / _  _/  
\t/_____/  /___/   /____/   /_/    /_____/  /_/ |_/  /_____/  /_/ |_|   
\t_____________________________________________________________________

"""


def print_user_menu() -> None:
    """
    This function prints the graphical user interface (GUI) in the terminal,
    displaying the different functionalities that Twitch Chat Listener offers.
    """

    # Execute the clear command in the terminal.
    subprocess.run(["clear"])

    print(ASCII_HEADER)

    print("\t1.- Sentiment analysis on Twitch streamings chats.")
    print("\t2.- Check Twitch streamings status [ON/OFF].")
    print("\t3.- List the last 'n' raw messages.")
    print("\t4.- List the last 'n' processed messages.")
    print("\t5.- Exit Twitch Chat Listener.")
