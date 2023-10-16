#!/bin/bash

## Modified from Andrew's script

# r = submit script
# n = number reps to stack
# a = id to 

add_id=""
num_reps=3  # set a max num?
runscript="this_script_does_not_exist.sh"

while getopts r:n:a: OPT; do
    case "${OPT}" in
        r)
            runscript=$OPTARG
            ;;
        n)
            num_reps=$OPTARG
            ;;
        a)
            add_id=$OPTARG
            ;;
    esac
done

echo "queuing ${num_reps} jobs of ${runscript}"

# first job
if [ -z "$add_id" ]; then
    echo "starting new chain"
    submit_job=$(qsub $runscript | cut -d' ' -f3)
else
    echo "adding behind job ${add_id}"
    submit_job=$(qsub -hold_jid $add_id $runscript | cut -d' ' -f3)
fi

echo $submit_job
submit_job="${submit_job%.*}"
echo $submit_job


# now loop to submit the rest
for id in $(seq 2 $num_reps); do
    submit_next=$(qsub -hold_jid $submit_job $runscript | cut -d' ' -f3)
    submit_job="${submit_next%.*}"
    echo $submit_job
done
