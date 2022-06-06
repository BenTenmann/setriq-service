# setriq-service

The functionalities of [setriq](https://github.com/BenTenmann/setriq) provided as a Seldon service in a Helm chart.
Assuming a running Kubernetes cluster, the service can be installed by running the following in the root of this
repository:

```bash
helm install `basename $PWD` helm/
```

Pairwise distances can then be computed by running the following:

```bash
# port forward service
kubectl port-forward svc/`basename $PWD` 9000 &

# send post request for a batch of sequences
curl -X POST localhost:9000/api/v1.0/predictions \
    -H 'Content-Type: application/json' \
    -d '{"sequences": ["CASSLKPNTEAFF", "CASSAHIANYGYTF", "CASRGATETQYF"]}'
```

This will return a JSON object with a single field `distances`, which is a JSON array of floats. In this case, this
array will be of length 1, as $n * \frac{n - 1}{2} = 1$, where $n$ is the number of sequences.

The distances returned in this case are Levenshtein distances. This is because this is the default metric of the
service (defined in `setriq_service/default_metric_spec.json`). However, any of the distance functions implemented in
`setriq` can be used, simply by specifying the `spec` field in the POST request:

```bash
curl -X POST localhost:9000/api/v1.0/predictions \
     -H 'Content-Type: application/json' \
     -d '{
            "sequences": ["CASSLKPNTEAFF", "CASSAHIANYGYTF", "CASRGATETQYF"],
            "spec": {"id": "CdrDist", "param": {"gap_opening_penalty": 5.0, "gap_extension_penalty": 2.0}}
     }'
```

Here we have specified the distance function to be `CdrDist` with the custom parameters under the `param` field. Note
that the `param` field is optional, as long as the corresponding class from `setriq` does not require those parameters
at initialisation.
