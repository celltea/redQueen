#strips off discord formatting so even @'s of channels can still be used for command inputs

def strip(fancy):
    fancy = fancy[2:-1]
    while not fancy.isdigit():
        if not fancy:
            return(None)
        fancy = fancy[1:]
    return(fancy)
