#!/bin/python2.7
#vampy is a minimal python tool for proccess dumping

# vampy is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

#FRIDA USED AS FRAMEWORK https://github.com/frida https://github.com/frida/frida
#BASED ON FRIDUMP https://github.com/Nightbringer21/fridump

version = 0.2

#Functions de Bibliotecas Default do Python
#importa funcoes de regex
import re
#importa funcao de manipulacao de argumento de inicializacao e standard output
from sys import argv, stdout
#importa chamadas de OS, chamar igual na linguagem C, system('comando do sistema')
from os import system
#Caso nao consiga importar o modulo de framework para qual a ferramenta depende, dar opcao de instala-lo
try:
	import frida
except:
	opt = raw_input("frida framework is required to run vampy, install(pip required)? [y/n]")
	if opt.lower() == "y" or opt.lower() == "yes":
		try:
			system("pip install frida")
		except Exception as e:
			print "[!] Exception caught: {}".format(e)
	else:
		print "[-] Aborting ..."
		exit(0)

help = """\n
VAMPY - Minimal tool for RAM dumping.

usage:
  -o, --output <DIRECTORY/PATH>		Output directory to store dump results
					(strings of all dumped data will be sa
					ved in the local directory)

  -u, --usb				Specify that the dump will be made on USB connected device.

  -p, --process <NAME>			Name of application to dump

tips:
  Use frida-ps to get process names and PIDs

e.g:
  $python vampy.py -p firefox-esr
"""

banner = """\n
   )        )      )             (
  /((    ( /(     (      `  )    )\ )
 (_))\   )(_))    )\  '  /(/(   (()/(
 _)((_) ((_)_   _((_))  ((_)_\   )(_))
 \ V /  / _` | | '  \() | '_ \) | || |
  \_/   \__,_| |_|_|_|  | .__/   \_, |
                        |_|      |__/
"""

#Perfumaria
def LoadingCallBack(j,k):
	stdout.write("\r [+] Files: [{}] (strings: [{}])".format(j,k))
	stdout.flush()

def DumpMemory(process, output):
	#O que tiver LoadingCallBack eh PERFUMARIA
	#arquivos
	j = 0
	#strings
	k = 0

	try:
		#Attach ao processo e comeca a utilizar a biblioteca de objetos/funcoes/atributos frida.
		print "\n [+]Attaching to process: {}\n".format(process)
		if not usb:
			attached_process = frida.attach(process)
		else:
			attached_process = frida.get_usb_device().attach(process)
	#Caso ocorra excecao, armazena output na variavel e
	except Exception as e:
		#metodo: .format preenche o valor nas chaves "{}" dentro da string
		print "[!] Exception caught 1, a bug may need to be fixed: {}".format(e)
		exit(0)

	#Busca apenas read-only
	process_memory = attached_process.enumerate_ranges('r--')
	for memory in process_memory:
		LoadingCallBack(j,k)
		try:
			#Faz o dump a partir do endereco base ate o tamanhano total do range de memoria utilizando metodo do modulo frida
			dump = attached_process.read_bytes(memory.base_address, memory.size)
			#Abre arquivo de log como escrita 'wb'
			f = open("{}-vampy/{}.dump".format(output,str(hex(memory.base_address))), 'wb')
			f.write(dump)
			f.close()
			j += 1
			LoadingCallBack(j,k)
		except Exception as e:
			print "\n[!] Memory Access Violation:{}".format(str(hex(memory.base_address)))
			print "\n[?] Info: {}".format(e)
			continue

		#Regex para filtrar strings memoria por memoria, similar ao comando strings e logar em um unico arquivo
		Raw = open("{}-vampy/{}.dump".format(output,str(hex(memory.base_address)))).read()
		strings_found = re.findall("[A-Za-z0-9/\-:;.,_$%'!()[\]<> \#]+",Raw)
		f = open("vampy.dump".format(output),"a+")
		for string in strings_found:
			if len(string) > 4:
				k += 1
				LoadingCallBack(j,k)
				f.write("{}\n".format(string))
		f.close()
	print "\nDone."


#Statement idiomatico do Python que verifica se o script esta sendo executado diretamente ou sendo importado por outro script ( https://docs.python.org/2/library/__main__.html )
if __name__ == "__main__":
	try:
		#Parse dos argumentos na inicializacao do programa
		process = None
		usb = False
		output = "output"
		for x in argv:

                        if x == "-h" or x == "--help":
                                print banner
                                print help
                                exit(0)

                        if x == "-p" or x == "--process":
				#argumento: string apos o -p com o nome do processo para realizar o dump
                                process = argv[argv.index(x) + 1]

			if x == "-o" or x == "--output":
				output = argv[argv.index(x) + 1]

			if x == "-u" or x == "--usb":
				usb = True

		if process:
				#Arquivo default de output
				system("mkdir {}-vampy".format(output))
				system("echo > vampy.dump".format(output))
				print banner
				#inicia a function de dump de memoria com o processo e o diretorio para redirecionar o resultado passados de parametros
				DumpMemory(process,output)
		else:
			print banner
			print "-h or --help	for instructions."

	#CTRL+C
	except KeyboardInterrupt:
			print "\n[!] Aborted..."
	except Exception as e:
			print "\n[!] Exception caught 2, a bug may need to be fixed: {}".format(e)

