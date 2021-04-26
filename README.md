# BestBuy-ShopBot
Because GPUs are hard to come by

To use this you can add a config.yaml file

I've included a config-example.yaml file for the fields. Save as a new config.yaml file in the same directory. Fill this out with your information but KEEP IT PRIVATE.

This project can be run in PyCharm. https://www.jetbrains.com/pycharm/download/

Additional Notes:
- You can add additional items or change the urls to search for RTX 20## series if desired. (See line 20 & 25: in bot.py to see how to add more BestBuy pages to scrape)
- Be sure to change the webdriver executable_path to your own local environment (See line 109: in bot.py)
- Configuration parameters can be added and used via PyYaml
