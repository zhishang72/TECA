#include "array_source.h"
#include "array.h"

#include "array.h"

#include <iostream>
#include <sstream>
#include <algorithm>

using std::vector;
using std::string;
using std::ostringstream;
using std::cerr;
using std::endl;

// --------------------------------------------------------------------------
array_source::array_source() :
    array_size(0),
    number_of_timesteps(0)
{
    this->set_number_of_inputs(0);
    this->set_number_of_outputs(1);
}

// --------------------------------------------------------------------------
array_source::~array_source()
{}

// --------------------------------------------------------------------------
void array_source::set_number_of_arrays(unsigned int n)
{
    if (this->array_names.size() != n)
    {
        this->array_names.clear();
        for (unsigned int i = 0; i < n; ++i)
        {
            ostringstream oss;
            oss << "array_" << i;
            this->array_names.push_back(oss.str());
        }
        this->set_modified();
    }
}

// --------------------------------------------------------------------------
teca_meta_data array_source::get_output_meta_data(
    unsigned int port,
    std::vector<teca_meta_data> &input_md)
{
    cerr << "array_source::get_output_meta_data" << endl;

    teca_meta_data output_md;

    // report time
    vector<double> time;
    for (unsigned int i = 0; i < this->number_of_timesteps; ++i)
        time.push_back(0.01*(i+1));
    output_md.set_prop("time", time);

    // report array extents
    vector<unsigned int> extent = {0, this->array_size};
    output_md.set_prop("extent", extent);

    // report array names
    output_md.set_prop("array_names", this->array_names);

    return output_md;
}

// --------------------------------------------------------------------------
p_teca_dataset array_source::execute(
    unsigned int port,
    std::vector<p_teca_dataset> &input_data,
    teca_meta_data &request)
{

    // get the time request
    double active_time;
    if (request.get_prop("time", active_time))
    {
        TECA_ERROR("request is missing time")
        return p_teca_dataset();
    }

    // get array request
    string active_array;
    if (request.get_prop("array_name", active_array))
    {
        TECA_ERROR("request is missing array_name")
        return p_teca_dataset();
    }

    vector<string>::iterator it
        = std::find(
            this->array_names.begin(),
            this->array_names.end(),
            active_array);

    if (it == this->array_names.end())
    {
        TECA_ERROR(
            << "invalid array \"" << active_array << "\" requested");
        return p_teca_dataset();
    }
    size_t array_id = it - this->array_names.begin();

    // get the extent request
    vector<size_t> active_extent;
    if (request.get_prop("extent", active_extent))
    {
        TECA_ERROR("request is missing extent")
        return p_teca_dataset();
    }

    // generate the a_out array
    p_array a_out = array::New();
    a_out->set_extent(active_extent);
    a_out->set_name(active_array);

    for (unsigned int i = active_extent[0]; i < active_extent[1]; ++i)
        a_out->append(array_id + active_time);

    cerr << "array_source::execute array=" << active_array
        << " time=" << active_time << " extent=["
        << active_extent[0] << ", " << active_extent[1]
        << "]" << endl;

    return a_out;
}
