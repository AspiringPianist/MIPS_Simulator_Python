.text
    # Load array base address
    addi $s0,$zero, 0x2000
    addi $t5, $zero, 1
    
    addi $t0, $zero, 1
    sw $t0, 0($s0)
    
    addi $t0, $zero, 2
    sw $t0, 4($s0)
    
    addi $t0, $zero, 3
    sw $t0, 8($s0)
    
    addi $t0, $zero, 4
    sw $t0, 12($s0)
    
    addi $t0, $zero, 5
    sw $t0, 16($s0)
    
    addi $t0, $zero, 5
    sw $t0, 20($s0)

    # Load array size
    lw $s1, 20($s0)

    # Initialize sum to 0
    addi $t0,$zero, 0

    # Loop through the array to calculate sum
    loop:
        # Check if we have reached the end of the array
        beq $s1, $zero, end_loop

        # Load the current element of the array
        lw $t1, 0($s0)

        # Add the current element to the sum
        add $t0, $t0, $t1

        # Move to the next element of the array
        addi $s0, $s0, 4

        # Decrement the counter
        sub $s1, $s1, $t5

        # Repeat the loop
        j loop

    end_loop:
    # $t0 now holds the sum of the array elements

    # Exit program
    addi $v0,$zero,  10       # syscall code for exit
    syscall
