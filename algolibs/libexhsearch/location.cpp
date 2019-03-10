#include "location.h"

namespace graph {

Location::Location(int row, int column) : row_(row), column_(column)
{
}

const Location Location::operator+(const OffsetType & offset) const
{
    return Location(row_ + offset.rowOffset, column_ + offset.columnOffset);
}

const Location & Location::operator+=(const OffsetType & offset)
{
    row_ += offset.rowOffset;
    column_ += offset.columnOffset;
    return *this;
}

bool Location::operator==(const Location & rhs) const
{
    return row_ == rhs.row_ && column_ == rhs.column_;
}

bool Location::operator!=(const Location & rhs) const {
    return !(*this == rhs);
}

bool Location::operator<(const Location & rhs) const {
    if (row_ < rhs.row_) return true;
    if (row_ > rhs.row_) return false;
    return column_ < rhs.column_;
}

int Location::getRow() const
{
    return row_;
}

int Location::getColumn() const
{
    return column_;
}

} // namespace graph
