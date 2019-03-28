import Ice, sys, time

def connectICEProxy(stringProxy, _class, tries=4):
    ic = Ice.initialize(sys.argv)
    i = 0
    while (True):
        try:
            i += 1
            basePrx = ic.stringToProxy(stringProxy)
            proxy = _class.checkedCast(basePrx)
            print("Connection Successful: ", stringProxy)
            break
        except Ice.Exception as e:
            if i is tries:
                print("Cannot connect to the proxy: ", stringProxy)
                return None
            else:
                time.sleep(1.5)
    return proxy