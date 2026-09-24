import json,sys
from .heritage import HeritageRegistry,ConservationGate
def main():
 r=HeritageRegistry.load(sys.argv[1]); print(json.dumps(ConservationGate(r).evaluate(),indent=2))
if __name__=="__main__": main()
