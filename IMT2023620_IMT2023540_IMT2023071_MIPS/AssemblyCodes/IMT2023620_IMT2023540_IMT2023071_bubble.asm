.text
    # Load array base address
    addi $s0,$zero, 0x2000

    # Load array size (4 times the number of elements in the array)
    addi $s1, $zero, 40

    addi $t0, $zero, 10
    sw $t0, 0($s0)

    addi $t0, $zero, 2
    sw $t0, 4($s0)

    addi $t0, $zero, 5
    sw $t0, 8($s0)

    addi $t0, $zero, 4
    sw $t0, 12($s0)

    addi $t0, $zero, 3
    sw $t0, 16($s0)

    addi $t0, $zero, 6
    sw $t0, 20($s0)

    addi $t0, $zero, 7
    sw $t0, 24($s0)

    addi $t0, $zero, 8
    sw $t0, 28($s0)

    addi $t0, $zero, 4
    sw $t0, 32($s0)

    addi $t0, $zero, 10
    sw $t0, 36($s0)

    jal bubble_sort

    # Exit program
    addi $v0,$zero, 10       # syscall code for exit
    syscall

bubble_sort:
    addi $t0, $zero, 0         # i = 0
outer_loop:
    sub $t6, $s1, $t0          # t6 = n - i
    addi $t6, $t6, -4          # t6 = n - i - 4
    beq $t6, $zero, end_bubble # if n - i == 4, exit outer loop

    addi $t1, $zero, 0         # j = 0
inner_loop:
    beq $t1, $t6, next_outer  # if j == n - i - 4, go to next outer iteration

    # Load arr[j] into $t2
    add $t7, $s0, $t1           # base address + offset
    lw $t2, 0($t7)

    # Load arr[j+1] into $t3
    addi $t8, $t1, 4            # j + 4
    add $t8, $s0, $t8           # base address + offset
    lw $t3, 0($t8)

    # Compare arr[j] and arr[j+1]
    #bge $t2, $t3, no_swap       # if arr[j] >= arr[j+1], no swap needed
    slt $at, $t2, $t3
    beq $at, $zero, no_swap

    # Swap arr[j] and arr[j+1]
    sw $t3, 0($t7)
    sw $t2, 0($t8)

no_swap:
    addi $t1, $t1, 4            # j += 4 (increment by word size)
    j inner_loop

next_outer:
    addi $t0, $t0, 4            # i += 4 (increment by word size)
    j outer_loop

end_bubble:
    jr $ra                       # return to caller
