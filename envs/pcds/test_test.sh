while read package; do
   echo "Running Tests for ${package}"
   pytest --benchmark-skip --pyargs "${package}"
done < package-tests.txt

