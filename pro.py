def isPalindrome(str):

    a, b = 0, len(str) - 1
    while a < b:
        while a < b and not alphaNum(str[a]):
            a += 1
        while a < b and not alphaNum(str[b]):
            b -= 1
        if str[a].lower() != str[b].lower():
            return False
        a += 1
        b -= 1
    return True




def alphaNum(self, c):
    return ( ord('a') <= ord(c) <= ord('z')) or (ord('0') <= ord(c) <= ord('9') or (ord('A') <= ord(c) <= ord('Z')))
