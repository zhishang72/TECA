#ifndef array_executive_h
#define array_executive_h

#include "teca_algorithm_executive.h"
#include "teca_meta_data.h"

#include <memory>
#include <vector>

class array_executive;
typedef std::shared_ptr<array_executive> p_array_executive;

class array_executive : public teca_algorithm_executive
{
public:
    TECA_ALGORITHM_EXECUTIVE_STATIC_NEW(array_executive)

    virtual int initialize(const teca_meta_data &md);
    virtual teca_meta_data get_next_request();

protected:
    array_executive(){}

private:
    std::vector<teca_meta_data> requests;
};

#endif
