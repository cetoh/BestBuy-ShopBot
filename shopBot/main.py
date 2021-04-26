# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import bot
import yaml


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm BestBuy Shop Bot')
    items_bought = 0
    item_max = 1

    # This will ensure a restart in case of network disconnect but only if you haven't actually bought something yet
    while items_bought < item_max:
        try:
            # Run main bot command. You can modify this string value to what you want
            bot.main('GeForce RTX 30')
        except Exception:
            print(Exception)

        config = yaml.safe_load(open('config.yaml', 'r'))
        item_max = config.get('MAX_TO_BUY')
        items_bought = config.get('AMT_BOUGHT')

    print(f'Bot Completed Tasks')
