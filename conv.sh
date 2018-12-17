SRCDATA="/Users/mlincoln/Development/dh_abstracts/dh_conferences/adho_fixture.json"

TGTDATA="/Users/mlincoln/Development/dh_abstracts/dh_web/app/abstracts/fixtures/adho_fixture.json"

iconv -c -f utf-8 -t ascii//TRANSLIT < $SRCDATA | sed -e 's/"/\"/g' > $TGTDATA

# CP $SRCDATA $TGTDATA