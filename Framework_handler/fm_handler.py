# Framework Handler (Which will link all the pieces of framework at once place)
import time
import Framework_component.xss_framework
from colorama import Style, Fore



def main():
    while True:
        print("Welcome to the X3r0Day Framework!")
        time.sleep(.2)
        opt1 = int(input("1 = XSS Scanner\n2 = SQLi Scanner\n99 = EXIT\n> "))
        if opt1 == 1:
            Framework_component.xss_framework.main()
        
        elif opt1 == 2:
            # Selected SQLi Scanner
            print()
        
        elif opt1 == 99:
            print("Exiting")
            time.sleep(.5)
            exit()

        else:
            print("Error! Please try again!")


if __name__ == "__main__":
    main()