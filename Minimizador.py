#!/usr/bin/env python
# -*- coding: utf-8 -*-
PALAVRA_FORA_DO_ALFABETO=0
PALAVRA_COM_TRANSICAO_INVALIDA=1
PALAVRA_NAO_CHEGOU_NO_ESTADO_FINAL=2
PALAVRA_ACEITA=3
import copy
import sys
'''
	ESTE SOFTWARE RODA TANTO NO PYTHON 2.x QUANTO NO 3.x
	EXEMPLO DE EXECUÇÃO EM BASH
		> python Minimizador.py [caminho do arquivo de entrada] [caminho do arquivo de saida]
	SOFTWARE TOTALMENTE DESENVOLVIDO PELO GRUPO PARA A DISCIPLINA DE TEORIA DA COMPUTAÇÃO
		> Lucas Batista Fialho - 2712
		> Wisney Bernardes - 1285
		> Marciley Oliveira - 2768
'''
'''
	Classe que representa um AFD
	TENDO COMO ATRIBUTOS:
		O ALFABETO ACEITO:TIPO LIST<string or numeric> sera convertido para LIST<string>
		CONJUNTO DE ESTADOS DO AFD:TIPO LIST<string or numeric> sera convertido para LIST<string>
		ESTADO INICIAL:ENTRADA PODE SER TANTO INTEIRA QUANTO STRING MAS TODAS AS MANIPULAÇOES SERAM FEITAS COMO ELA SENDO STRING.
		CONJUNTO DE ESTADOS FINAIS:TIPO LIST<string or numeric> sera convertido para LIST<string>
	NÃO É PRECISO PASSAR AS TRANSIÇÕES NO CONSTRUTOR, AS MESMAS SERAM FEITAS ATRAVES DO USO DO METODO ftransicao(e1,ch,e2).
'''
class AFD:
	def __init__(self,alfabeto,estados,inicial,final):
		self.alfabeto=[]#tipo lista
		for i in range(0,len(alfabeto)):
			self.alfabeto.append(str(alfabeto[i]))
		self.estados=[]#tipo lista
		for i in range(0,len(estados)):
			self.estados.append(str(estados[i]))
		self.transicao={}#tipo dict para melhor representação de grafos
		self.inicial=str(inicial)#tipo string representa o estado inicial
		self.final=[]#tipo lista representa todos os estados finais do AFD
		for i in range(0,len(final)):
			self.final.append(str(final[i]))
    #função de transição de um estado lendo um terminal para outro estado
	def ftransicao(self,e1,ch,e2):
		if(e1 in self.transicao):
			trans=self.transicao[str(e1)]
			trans[str(ch)]=str(e2)
		else:
			self.transicao[e1]={str(ch):str(e2)}
	def reconhece(self,palavra):
		estado=self.inicial
		out={}
		for i in range(0,len(palavra)):
			
			if(palavra[i] not in self.alfabeto):
				out={'status':False,'motivo':PALAVRA_FORA_DO_ALFABETO}
				return out

			elif(estado not in self.transicao or palavra[i] not in self.transicao[estado]):
				out={'status':False,'motivo':PALAVRA_COM_TRANSICAO_INVALIDA}
				return out
			else:
				estado=self.transicao[estado][palavra[i]]
		if estado not in self.final:
			
			out={'status':False,'motivo':PALAVRA_NAO_CHEGOU_NO_ESTADO_FINAL}
		else:
			out={'status':True,'motivo':PALAVRA_ACEITA}
		return(out)
	
class Minimizador:
	def __init__(self,afd):
		self.afd=afd#AFD para ser minimizado
		self.table={}#tabela de minimização
		self.lista={}#lista auxiliar de estados pendentes para equivalencia.
	'''
		[PRE-REQUISITO PARA MINIMIZAÇÃO]
		Metodo responsavel por verificar todas as transições indefinidas e criar se for preciso o 
		estado D de não aceitação.
		[RETORNO a instancia da classe atual,para poder fazer chamadas de metodos encadeados]
	'''
	def transicao_indefinida(self):
		for estado in self.afd.estados:
			for ltr in self.afd.alfabeto:
				if estado not in self.afd.transicao or ltr not in self.afd.transicao[estado]:
					if 'd' not in self.afd.estados:
						self.afd.estados.append('d')
					self.afd.ftransicao(estado,ltr,'d')
					self.afd.ftransicao('d',ltr,'d')
		return self
	'''
		[PRE-REQUISITO PARA MINIMIZAÇÃO]
		Metodo responsavel por identificar e remover os estados pelos quais não são acessiveis
		apartir do estado inicial.
		[RETORNO a instancia da classe atual,para poder fazer chamadas de metodos encadeados]
	'''
	def estado_inacessivel(self):
		for i in range(0,len(self.afd.estados)):
			estado=self.afd.estados[i]
			status=False
			if estado == self.afd.inicial:
				status=True
				continue

			for e in self.afd.transicao:#percorre todas as transiçoes.
				
				for ltr in self.afd.alfabeto:#percorre o alfabeto
					if self.afd.transicao[e][ltr]==estado:#verifica se existe transição dado o estado e e um terminal para o estado em questão.
						status=True#SE EXISTE ENTÃO É TRIVIAL PERCORRER TODO ALFABETO.
						break
			if status==False:#se o status for igual a false significa que o estado i não é alcançavel.
				del self.afd.transicao[self.afd.estados[i]]#remove as transições do estado inacessivel.
				del self.afd.estados[i]#remove o estado inalcançavel
				self.estado_inacessivel()#verifica se existe mais estados inacessiveis[CHAMADA RECURSIVA]
				break
		return self
	'''
		[ETAPA 1-MINIMIZAÇÃO]
		É CRIADO UMA TABELA DE MINIMIZAÇÃO SEGUINDO O MODELO PROPOSTO NO LITERATURA.
		MARCANDO TAMBEM OS ESTADOS QUE TRIVIALMENTE NÃO PODEM SER EQUIVALENTES.
		QUE SÃO ELES [ESTADO FINAL X ESTADO NÃO FINAL] E [ESTADO NÃO FINAL X ESTADO FINAL]
		[RETORNO a instancia da classe atual,para poder fazer chamadas de metodos encadeados]

	'''
	def preenche_tabela(self):
		self.table={}
		for i in range(0,len(self.afd.estados)):
			for j in range(0,i):
				if (self.afd.estados[j] in self.afd.final and  self.afd.estados[i] not in self.afd.final) or (self.afd.estados[i] in self.afd.final and  self.afd.estados[j] not in self.afd.final):
					#marcar
					res='X'
				else:
					#não marcar
					res=None
				if self.afd.estados[i] in self.table:
					aux=self.table[self.afd.estados[i]]
					aux[self.afd.estados[j]]=res
				else:
					self.table[self.afd.estados[i]]={self.afd.estados[j]:res}
		return self
	'''
		@USADO NO METODO verifica_estados_nao_marcados()
		[Parte integrante da checagem de equivalencia de estados não trivialmente marcados]
		@parametros[dois estados diferentes]
		Metodo de verificação de equivalencia entre dois estados,caso eles não sejam equivalentes
		terá dois destinos possiveis adição em uma lista auxiliar ou se o estado da transição de um for 
		para um estado marcado então marca na tabela e1,e2 e se o mesmo encabeçar uma lista marca toda 
		cauda.  
	'''
	def checa_equivalencia(self,e1,e2):
		i=0
		for ch in self.afd.alfabeto:
			if self.afd.transicao[e1][ch] == self.afd.transicao[e2][ch]:
				i=i+1
				
			elif (self.afd.transicao[e1][ch] in self.table and self.afd.transicao[e2][ch] in self.table[self.afd.transicao[e1][ch]]):
				if self.table[self.afd.transicao[e1][ch]][self.afd.transicao[e2][ch]]=='X':
					
					self.table[e1][e2]='X'
					if str(self.afd.transicao[e1][ch])+','+str(self.afd.transicao[e2][ch]) in self.lista:
						#entao vamos marcar todos da lista.
						
						for tail in self.lista[str(self.afd.transicao[e1][ch])+','+str(self.afd.transicao[e2][ch])]:
							
							estado1=tail.split(',')[0].strip()
							estado2=tail.split(',')[1].strip()
							self.table[estado1][estado2]='X'
						del(self.lista[str(self.afd.transicao[e1][ch])+','+str(self.afd.transicao[e2][ch])])


				else:
					if str(self.afd.transicao[e1][ch])+','+str(self.afd.transicao[e2][ch]) not in self.lista:
						self.lista[str(self.afd.transicao[e1][ch])+','+str(self.afd.transicao[e2][ch])]=[str(e1)+','+str(e2)]
					else:
						self.lista[str(self.afd.transicao[e1][ch])+','+str(self.afd.transicao[e2][ch])].append(str(e1)+','+str(e2))
	'''
		@depende das etapas anteriores da minimização
		@é chamado pelo metodo minimiza()
		[ETAPA 2 - MINIMIZAÇÃO]
		VERIFICA PARA CADA PAR DE ESTADOS DA TABELA NO QUAL NÃO FOI MARCADO.
		E COM ISSO CHAMA O METODO DE VERIFICAÇÃO DE EQUIVALENCIA DO PAR DE ESTADOS.

	'''					
	def verifica_estados_nao_marcados(self):
		for i in self.table:
			for j in self.table[i]:
				if self.table[i][j]==None:
					self.checa_equivalencia(i,j)

			
	'''
		[ETAPA PRINCIPAL]
	'''
		
	def minimiza(self):
		#CRIA ESTADO D PARA TODAS AS TRANSIÇÕES INDEFINIDAS
		#REMOVE TODOS OS ESTADOS INACESSIVEIS APARTIR DO ESTADO INICIAL
		#Preenche a tabela de estados com dados iniciais.
		self.transicao_indefinida().estado_inacessivel().preenche_tabela()
		#Agora temos que analizar os estados que não estão marcados(None)
		self.verifica_estados_nao_marcados()
		
		
		self.afd=self.joinStates()
		self.transicao_indefinida()
		
		return self.afd
	'''
		[NÃO FAZ PARTE DOS PROCESSOS DA MINIMIZAÇÃO,É APENAS UM METODO RAPIDO]
		METODO AUXILIAR PARA UNIÃO DE DUAS LISTAS DO TIPO DICIONARIO.
		@USADO NO METODO joinSatates
		[RETORNA UMA LISTA DO TIPO DICIONARIO COM A UNIÃO DOS ITENS DOS DOIS DICIONARIOS]
	'''
	def union(self,dict1, dict2):return dict(list(dict1.items()) + list(dict2.items()))
	'''
		@DEPENDE DA EXECUÇÃO DAS ETAPAS ANTERIORES
		[ETAPA 3 - MINIMIZAÇÃO]
		Junção de estados equivalentes, criando novo estado que conterá todas as transições dos dois estados equivalentes
		Todas as transiçoes que referenciavam os estados antigos passaram a referenciar o novo estado
		Remoção dos estados equivalentes
		[RETORNA O NOVO AFD COM OS TODAS AS TAREFAS EXECUTADAS]@returnType(AFD)
	'''
	def joinStates(self):

		#duplica a instancia da classe minimizador sendo assim só mexemos com o objeto da classe copiada.
		newAfd=copy.copy(self.afd)
		for i in self.table:
			for j in self.table[i]:
				if self.table[i][j]==None:
					#junta os estados e remove os dois antigos transformando em unico com todas as transiçoes.
					newAfd.estados.append(str(j)+str(i))
					
					if j not in self.afd.transicao:
						transicaoj={}
					else:
						transicaoj=self.afd.transicao[j]
					if i not in self.afd.transicao:
						transicaoi={}
					else:
						transicaoi=self.afd.transicao[i]
					newAfd.transicao[str(j)+str(i)]=self.union(transicaoi,(transicaoj))
					'''AJUSTA AGORA TODOS AS TRANSIÇÕES ANTIGAS PARA O NOVO ESTADO'''
					for estado_atual in newAfd.transicao:
						for letra in newAfd.transicao[estado_atual]:
							if i in newAfd.transicao[estado_atual][letra] or j in newAfd.transicao[estado_atual][letra]:
								newAfd.transicao[estado_atual][letra]=str(j)+str(i)
					if i == newAfd.inicial or j == newAfd.inicial:
						newAfd.inicial=str(j)+str(i)
					if i in newAfd.final or j in newAfd.final:
						if i in newAfd.final:
							del(newAfd.final[newAfd.final.index(i)])
						if j in newAfd.final:
							del(newAfd.final[newAfd.final.index(j)])
						newAfd.final.append(str(j)+str(i))


					if i in newAfd.transicao:
						del(newAfd.transicao[i])
						estado_rem=newAfd.estados.index(i)
						del(newAfd.estados[estado_rem])
					if j in newAfd.transicao:

						del(newAfd.transicao[j])
						estado_rem=newAfd.estados.index(j)
						del(newAfd.estados[estado_rem])
					
					continue
					
				else:
					#apenas copia.
					pass
		return newAfd

'''
	CLASSE RESPONSAVEL POR OPERAÇÕES DE LEITURA E ESCRITA NOS ARQUIVOS DE ENTRADA E SAIDA RESPECTIVAMENTE.
	[PARAMETROS DO METODO CONSTRUTOR] CAMINHO DO ARQUIVO DE ENTRADA E O DE SAIDA.
	Logo depois é feita a leitura do arquivo de entrada.
'''
class INOUT:
	def __init__(self,fileIN,fileOUT):
		self.fileIN=open(fileIN,'r')
		self.fileOUT=open(fileOUT,'w')
		self.readFile()
	#é feita a leitura linha a linha do arquivo de entrada
	def readFile(self):
		'''
			O uso do while true é pelo fato de ter linhas em branco antes dos dados relevantes.
		'''
		while True:
			linha=self.fileIN.readline()
			if (linha.split('#')[0].strip()) in ['AFN','GR']:
				status=False
				print('O NOSSO SOFTWARE SO CONSEGUE MINIMIZAR AUTOMATOS FINITOS DETERMINISTICOS!!!')
				break
			elif (linha.split('#')[0].strip())=='AFD':
				status=True
				break
		if status==False:
			return	
		while True:
			linha=self.fileIN.readline()
			if (linha.split('#')[0].strip()) not in [' ','',None,'0']:
				estados=range(0,int(linha.split('#')[0].strip()))
				break
		while True:
			linha=self.fileIN.readline()
			if (linha.split('#')[0].strip()) not in [' ','',None,'0']:
				terminais=range(0,int(linha.split('#')[0].strip()))
				break
		self.afd=AFD(terminais,estados,0,[0])
		for e in range(0,len(estados)):
			for t in range(0,len(terminais)):
				while True:
					linha=self.fileIN.readline()
					if (linha.split('#')[0].strip()) not in [' ','',None]:
						estado_chegada=linha.split('#')[0].strip()
						break
				if estado_chegada=='-1':
					continue

				self.afd.ftransicao(str(estados[e]),str(terminais[t]),estado_chegada)
		while True:
			linha=self.fileIN.readline()
			if (linha.split('#')[0].strip()) not in [' ','',None]:
				self.afd.inicial=str(linha.split('#')[0].strip())
				break
		while True:
			linha=self.fileIN.readline()
			if (linha.split('#')[0].strip()) not in [' ','',None]:
				final=str(linha.split('#')[0].strip())
				self.afd.final=[]
				for i in range(0,int(final)):
					linha=self.fileIN.readline()
					self.afd.final.append(str(linha.split('#')[0].strip()))
				break
		self.fileIN.close()
	#escrita no arquivo de saida do AFD minimizado.
	def save(self,afd):
		self.fileOUT.write("AFD\t# identifica o tipo de formalismo\n")
		self.fileOUT.write(str(len(afd.estados))+"\t# quantidade de estados\n")
		self.fileOUT.write(str(len(afd.alfabeto))+"\t# quantidade de símbolos terminais\n")
		for e in range(0,len(afd.estados)):
			for t in range(0,len(afd.alfabeto)):
				self.fileOUT.write(afd.transicao[afd.estados[e]][afd.alfabeto[t]]+"\t# Função de transição δ (q"+str(afd.estados[e])+", "+str(afd.alfabeto[t])+") = q"+afd.transicao[afd.estados[e]][afd.alfabeto[t]]+"\n")
		self.fileOUT.write(afd.inicial+"\t# estado inicial(q"+afd.inicial+")\n")
		self.fileOUT.write(str(len(afd.final))+"\t# quantidade de estados finais\n")
		for f in afd.final:
			self.fileOUT.write(f+"\t# estados finais\n")

		self.fileOUT.close()

if __name__ == "__main__":
	#tecnica para poder executar o software no python 3
	if len(sys.argv)<2:
		try:
			raw_input
		except NameError:
			raw_input=input
			pass
		InputFile=str(raw_input("Digite o caminho do arquivo de entradas:"))
		OutputFile=str(raw_input("Digite o caminho do arquivo de saidas:"))
	else:
		#caso tenha passado algum parametro via bash os mesmos são respectivamente a o arquivo de entrada e saida.
		InputFile=sys.argv[1]
		OutputFile=sys.argv[2]

	inputAFD=INOUT(InputFile,OutputFile)
	afd=inputAFD.afd
	minimizador=Minimizador(afd)
	nafd=minimizador.minimiza()
	inputAFD.save(nafd)
	print('AFD MINIMIZADO : \n %s'%nafd.transicao)
	print('AFD NO FORMATO CORRETO NO ARQUIVO DE SAÍDA '+OutputFile+' SALVO!!!')
