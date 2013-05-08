candidate-placer
================

Python engine to select and place candidates to satisfy most of the team needs

Idea
  Sometimes it is quite difficult to make decision how to divide N approved
  candidates to M teams based on team's requirements as some teams may be
  interested in the same candidate profile.
  
  The decision meeting with team representatives may be quite emotional, that's
  why I decided to write piece of software to calm down the discussion...
  

Example of usage:
  
  We have 5 accepted candidates Alice, Bob, Eve, Ann and Frank.
  We want to place above candidates to 4 teams tA, tB, tC, tD according
  following requirements (team wishlists):
    team tA: Alice (p1), Eve (p2), Bob (p3)
    team tB: Alice (p1), Bob (p2)
    team tC: Frank (p1), Bob (p2), Ann (p3)
    team tD: Eve (p1), Alice (p2), Frank (p3)
  
  During the negotiation was decided that Frank has to go to team tD.
  
  The tool configuration for above situation is:
    ./cplacer.py
      # control parameters
      --save-data=a.srl --list-all -s --solve-cnt 3
      # candidates
      -C 'Alice' -C 'Bob' -C 'Eve' -C 'Ann' -C 'Frank'
      # teams
      -T 'tA~1' -T 'tB~1~Nick"s team nick' -T 'tC~1' -T 'tD~2'
      # decisions
      -D 'tD~Frank'
      # team's requirements / wishlists
      -R 'tA~Alice~1' -R 'tA~Bob~3' -R 'tB~Bob~2' -R 'tB~Alice~1' -R 'tC~Ann~3' \
      -R 'tC~Bob~2' -R 'tD~Eve~1' -R 'tA~Eve~2' -R 'tD~Alice~2' -R 'tD~Frank~3' \
      -R 'tC~Frank~1'  

Requirements
  python 2.5+

Files
  cplacer.py                main python engine

License
  GPL v2
  http://www.gnu.org/licenses/gpl-2.0.html


.eof
