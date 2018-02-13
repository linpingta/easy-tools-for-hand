import argparse, os
import time

def main():
    print "hello world"
    time.sleep(3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='stack')
    parser.add_argument('--date',type=str)
    parser.add_argument('--neg_sample_rate',type=float, default=1.0)
    args = parser.parse_args()
    main()
