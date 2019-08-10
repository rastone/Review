strcpy:
subi $sp,$sp,4		 # make space on the stack
sw $s0,0($sp)		 # store $sp address to $s0
add $s0,$zero,$zero  # int i = 0

loop: 
add $t1,$s1,$s0      # address of s1[i]
lb $t3,0($t1) 	      # load byte s1[i] in $t3
add $t2,$s2,$s0      # address for s2[i]
sb $t3,0($t2) 	      # store byte s1[i] into s2[i]
addi $s0,$s0,1       # i = i + 1
bne $t2,$zero,loop 	 # if s1[i]!=0 go to loop
add $s2,$zero,$zero  # s2[i] = 0

exit:
addi $sp,$sp,4		 # return space to stack
jr $ra			 # return

