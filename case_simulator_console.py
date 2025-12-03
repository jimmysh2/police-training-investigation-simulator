#!/usr/bin/env python3
import json, sys
from pathlib import Path
case = json.load(open('case_demo_001.json'))

def run_interactive(case):
    print('\\nCASE SIMULATION: ' + case['title'])
    print(case['summary'])
    score = 0
    for i, stage in enumerate(case['stages'], start=1):
        print('\\n--- Stage %d:' % i)
        print(stage['info'])
        print('\\nQuestion: ' + stage['question'])
        for idx, opt in enumerate(stage['options']):
            print('  %d) %s' % (idx, opt))
        # interactive input
        try:
            ans = int(input('Enter option number: ').strip())
        except Exception:
            print('Invalid input — counted as wrong.')
            ans = -1
        if ans == stage['correct']:
            print('Correct. Proceeding...')
            score += 1
            print('Next:', stage['next_info'])
        else:
            print('Wrong. Feedback:', stage['feedback_wrong'])
            # allow one retry
            try:
                ans2 = int(input('Try again - enter option number: ').strip())
            except Exception:
                ans2 = -1
            if ans2 == stage['correct']:
                print('Correct on retry. Proceeding...')
                score += 0.5
                print('Next:', stage['next_info'])
            else:
                print('Wrong again. Revealing correct action:', stage['options'][stage['correct']])
                print('Next:', stage['next_info'])
    print('\\nSimulation ended. Score: %s/%d' % (score, len(case['stages'])) )


if __name__ == "__main__":
    run_interactive(case)
