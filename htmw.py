import sys
import os
from time import sleep
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

import traceback
import subprocess

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

from secrets import HTMW_USERNAME
from secrets import HTMW_PASSCODE


class Order:

	def __init__(self, market, action, symbol, quantity, _type):
		self.market = market
		self.action = action
		self.symbol = symbol
		self.quantity = quantity
		self._type = _type
		self.datetime = datetime.utcnow()


class Controller:

	def __init__(self):
		self.drvier = None

	def get_portfolio_info(self):
		try:
			self.driver.get('https://www.howthemarketworks.com/accounting/openpositions')
			try:
				self.authenticate()
			except Exception as e:
				pass

			sleep(3)
			self.driver.find_element_by_xpath('//*[@id="exchange-select"]/div[6]/a').click()
			sleep(1)
			self.driver.find_element_by_xpath('//*[@id="btnExport"]').click()
			sleep(4)

			t = self.htmw_date_today()
			ppath = f'{os.getcwd()}/portfolio/'
			filename = f'OpenPositions_{t}.csv'
			filepath = f'{os.path.join(Path.home(), "Downloads")}/{filename}'
			subprocess.call(['mv', filepath, ppath])

			return True
		
		except Exception as e:
			print('Unable to download portfolio.')
			self.destroy_window()
			return False
	

	def htmw_date_today(self):
		t = str(datetime.today().strftime("%m_%d_%Y"))
		m = t[0:2].replace('0', '')
		d = t[3:5].replace('0', '')
		return f'{m}_{d}{t[5:10]}'


	def place_orders(self, orders):
		try:
			self.driver.get('https://www.howthemarketworks.com/trading/equities')
			self.authenticate()
			sleep(1)
		except Exception as e:
			print('Unable to place orders.')
			return False

		for order in orders:
			try:
				self.fill_order_form(order)
				sleep(1)
				self.driver.refresh()

			except Exception as e:
				print(f'Unable to place order {order.symbol}.')

		return True


	def place_order(self, order):
		try:
			self.driver.get('https://www.howthemarketworks.com/trading/equities')
			self.authenticate()
			sleep(1)
			self.fill_order_form(order)
			sleep(1)
			self.driver.refresh()
			return True

		except Exception as e:
			print(f'Unable to place order {order.symbol}.')
			return False


	def fill_order_form(self, order):

		try:
			# Market
			if order.market == 'USD':
				self.driver.find_element_by_xpath('//*[@id="exchange-select"]/div[2]/a').click()
			elif order.market == "CAD":
				self.driver.find_element_by_xpath('//*[@id="exchange-select"]/div[3]/a').click()

			sleep(1)

			# Action
			if order.action == "BUY":
				action = 1
			elif order.action == "SELL":
				action = 2
			elif order.action == "SHORT":
				action = 3
			elif order.action == "COVER":
				action = 4
			else:
				return False

			#self.drvier.execute_script("document.getElementById('tbSymbol').setAttribute('value class', 'ui-autocomplete-input invalid')")
			Select(self.driver.find_element_by_xpath('//*[@id="ddlOrderSide"]')).select_by_value(str(action))
			sleep(1)

			# Symbol
			#self.driver.find_element_by_xpath('//*[@id="tbSymbol"]').send_keys(order.symbol)
			self.driver.find_element_by_xpath('//*[@id="tbSymbol"]').send_keys(order.symbol)
			self.driver.find_element_by_xpath('//*[@id="exchange-select"]').click()
			sleep(2)

			# Quantity
			self.driver.find_element_by_xpath('//*[@id="tbQuantity"]').send_keys(order.quantity)
			self.driver.find_element_by_xpath('//*[@id="exchange-select"]').click()
			sleep(1)

			# Type
			Select(self.driver.find_element_by_xpath('//*[@id="ddlOrderType"]')).select_by_value(str(order._type))
			sleep(1)

			# Preview order
			self.driver.find_element_by_xpath('//*[@id="btn-preview-order"]').click()
			sleep(1)

			# Confirm order
			self.driver.find_element_by_xpath('//*[@id="btn-place-order"]').click()

			sleep(1)
			#self.driver.refresh()

			return True

		except Exception as e:
			print("Unable to fill order form.")
			return False


	def create_window(self):

		try:
			self.driver = webdriver.Safari(executable_path = "/usr/bin/safaridriver")
		
			self.driver.get('https://www.howthemarketworks.com/login')
			#self.driver.get('https://www.howthemarketworks.com/trading/equities')

			self.driver.maximize_window()

			#self.authenticate()
			
		except:
			print('Unable to create window.')
			self.destroy_window()
		

	def destroy_window(self):
		self.driver.quit()
		

	def authenticate(self):

		try:
			self.driver.find_element_by_xpath('//*[@id="UserName"]').send_keys(HTMW_USERNAME)
			sleep(1)
			self.driver.find_element_by_xpath('//*[@id="Password"]').send_keys(HTMW_PASSCODE)
			sleep(1)
			self.driver.find_element_by_xpath('//*[@id="RememberMe"]').click()
			self.driver.find_element_by_xpath('/html/body/section/div/div/div[3]/form/input[6]').click()

		except:
			print("Unable to authenticate.")
			#self.destroy_window()
