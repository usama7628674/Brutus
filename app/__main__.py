import inquirer
import threading
import os
import subprocess
import platform
from inquirer import errors
from utils.mac_changer import main as mac_changer
from utils.network_scanner import main as network_scan
from utils.arp_spoofer import main as arp_spoofer
from utils.packet_sniffer import main as packet_sniffer
try:
   from utils.dns_spoofer import main as dns_spoofer
except ImportError:
   pass

operating_sys = platform.system().lower()
dir_path = os.path.dirname(os.path.dirname(__file__))

def spawn_disparate_shell_linux(utility):
   """
   Initialize given utility as its own process, in a discrete shell.
   Enforces Linux-contingent validation.
   """
   if (operating_sys == "linux" or operating_sys == "linux2"):
      os.system(f"gnome-terminal -e 2>/dev/null 'bash -c \"python3 -m utils.{utility}.main; exec bash\"'")
   else:
      print("[-] Your operating system does not support this utility.\n")

def spawn_disparate_shell_unix(utility):
   """
   Initialize given utility as its own process, in a discrete shell.
   Enforces UNIX-contingent validation.
   """
   # imperfect solution for production, but launch in new terminal as root user
   if (operating_sys == "linux" or operating_sys == "linux2"):
      os.system(f"gnome-terminal -e 2>/dev/null 'bash -c \"python3 -m utils.{utility}.main; exec bash\"'")
   if (operating_sys == "darwin"):
      os.system(f"""osascript -e 'tell app "Terminal"
      do script "cd {dir_path}; python3 -m utils.{utility}.main"
      end tell' """)
   else:
      print("[-] Your operating system does not support this utility.\n")

def exit_status(answers):
   """
   Simulates sigkill on primary thread loop to exit app (somewhat) quietly.
   """
   return (answers["primary_thread"] == "exit")

def flag_processes(answers, current):
   """
   Flag certain processes to prompt the user for confirmation before proceeding.
   """
   if ("spoofer" in current or "sniffer" in current):
      response = inquirer.prompt([inquirer.Confirm('mitm', message="You must be established as MITM to run this module. Proceed?")])
      if (response["mitm"] == True):
         return True
      else:
         return False
   else:
      return True 

def main():
   primary_choices = [("Utilities", "utils"), "Payloads", "Leviathan C&C",("Exit","exit")]
   util_choices = [
      ("MAC Changer (Cloak)", "cloak"), 
      ("Network Scanner","network_scan"),
      ("ARP Spoofer", "arp_spoofer"),
      ("DNS Spoofer", "dns_spoofer"),
      ("Packet Sniffer", "packet_sniffer")
      ]

   questions = [
      inquirer.List("primary_thread", "Select an option", choices=primary_choices),
      inquirer.List("utils", "Select a Utility", choices=util_choices, ignore=exit_status, validate=flag_processes)
   ]

   while True:
      answers = inquirer.prompt(questions, raise_keyboard_interrupt=True)
      if (answers and answers["primary_thread"] == "exit"):
         break
      if (answers and answers["utils"] == "cloak"):
         mac_changer.main()
      if (answers and answers["utils"] == "network_scan"):
         network_scan.main()
      if (answers and answers["utils"] == "arp_spoofer"):
         spawn_disparate_shell_unix("arp_spoofer")
      if (answers and answers["utils"] == "dns_spoofer"):
         spawn_disparate_shell_linux("dns_spoofer")
      if (answers and answers["utils"] == "packet_sniffer"):
         spawn_disparate_shell_unix("packet_sniffer")
         
      print(answers)

if __name__ == "__main__":
   try:
      main()
   except KeyboardInterrupt:
      print("[-] Done.")
"""
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError


style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})
"""



   