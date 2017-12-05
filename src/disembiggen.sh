
sed 's/[|][[:space:]]*$//' $1

sed -i .old 's/\]\,/\]\
/g' $1