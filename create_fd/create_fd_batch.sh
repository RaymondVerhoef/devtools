if [ $1 ] && [ $2 ]
then
    # Load freightdocuments 
    for ((i=0; i<=$1-1; i++)); do
        echo "Insert freightdocument $(($i+1)) from JSon $2"
        python create_fd.py --json_file $2 
    done
else
    # Help
    echo ""
    echo "Shell script moet aangeroepen worden met onderstaande parameters:"
    echo "- Het aantal vrachtbrieven dat script moet toevoegen"
    echo "- De JSon file die gebruikt moet worden"
    echo ""
fi
