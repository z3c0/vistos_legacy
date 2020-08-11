"""Module for handling GPO query options"""
from typing import Optional


def is_valid_bioguide_position(position: Optional[str]) -> bool:
    """Returns true if the value given is a valid position"""
    valid_positions = set(p for p in vars(Position) if p[:2] != '__')
    return position is None or position in valid_positions


def is_valid_bioguide_party(party: Optional[str]) -> bool:
    """Returns true if the value given is a valid party"""
    valid_parties = set(p for p in vars(Party.Current) if p[:2] != '__')
    valid_parties = valid_parties.union(set(p for p in vars(Party.Historical)
                                            if p[:2] != '__'))
    valid_parties = valid_parties.union(set(p for p in vars(Party.Errors)
                                            if p[:2] != '__'))
    return party is None or party in valid_parties


def is_valid_bioguide_state(state: Optional[str]) -> bool:
    """Returns true if the value given is a valid state"""
    valid_states = set(s for s in vars(State) if s[:2] != '__')
    return state is None or state in valid_states


class Position:
    """Available options for member positions"""
    REPRESENTATIVE = 'Representative'
    SENATOR = 'Senator'
    DELEGATE = 'Delegate'
    VICE_PRESIDENT = 'Vice President'
    PRESIDENT = 'President'
    CONTINENTAL_CONGRESS = 'ContCong'
    SPEAKER_OF_THE_HOUSE = 'Speaker of the House'


class Party:
    """Available options for member parties"""
    class Current:
        """Currently-active parties"""
        DEMOCRAT = 'Democrat'
        INDEPENDENT = 'Independent'
        REPUBLICAN = 'Republican'

    class Errors:
        """Duplicate options caused by apparent data-entry errors"""
        ANTI_JACKSONIAN = 'Anti Jacksonian'
        ANTI_ADMINISTRATION = 'Anti-administration'
        CRAWFORD_REPUBLICAN = 'Crawford Republicans'
        DEMOCRAT_FARM_LABOR = 'Democrat-Farm Labor'
        DEMOCRAT_REPUBLICAN = 'Democrat;Republican'
        PRO_ADMINISTRATION = 'Pro-administration'

    class Historical:
        """Formerly-active parties"""
        ADAMS = 'Adams'
        ADAMS_REPUBLICAN = 'Adams Republican'
        ADAMS_CLAY_FEDERALIST = 'Adams-Clay Federalist'
        ADAMS_CLAY_REPUBLICAN = 'Adams-Clay Republican'
        ALLIANCE = 'Alliance'
        AMERICAN = 'American'
        AMERICAN = 'American (Know-Nothing)'
        AMERICAN_LABORITE = 'American Laborite'
        AMERICAN_PARTY = 'American Party'
        ANTI_ADMINISTRATION = 'Anti-Administration'
        ANTI_DEMOCRAT = 'Anti-Democrat'
        ANTI_JACKSONIAN = 'Anti-Jacksonian'
        ANTI_LECOMPTON_DEMOCRAT = 'Anti-Lecompton Democrat'
        ANTI_MASONIC = 'Anti-Masonic'
        ANTI_MONOPOLIST = 'Anti-Monopolist'
        COALITIONIST = 'Coalitionist'
        CONSERVATIVE = 'Conservative'
        CONSERVATIVE_REPUBLICAN = 'Conservative Republican'
        CONSTITUTIONAL_UNIONIST = 'Constitutional Unionist'
        CRAWFORD_FEDERALIST = 'Crawford Federalist'
        CRAWFORD_REPUBLICAN = 'Crawford Republican'
        DEMOCRAT_FARMER_LABOR = 'Democrat Farmer Labor'
        DEMOCRAT_LIBERAL = 'Democrat-Liberal'
        DEMOCRAT_INDEPENDENT = 'Democrat/Independent'
        DEMOCRAT_REPUBLICAN = 'Democrat/Republican'
        DEMOCRATIC_REPUBLICAN = 'Democratic Republican'
        DEMOCRATIC_AND_UNION_LABOR = 'Democratic and Union Labor'
        FARMER_LABORITE = 'Farmer Laborite'
        FEDERALIST = 'Federalist'
        FREE_SILVER = 'Free Silver'
        FREE_SOIL = 'Free Soil'
        FREE_SOILER = 'Free Soiler'
        GREENBACKER = 'Greenbacker'
        HOME_RULE = 'Home Rule'
        INDEPENDENCE_PARTY_MINNESOTA = 'Independence Party (Minnesota)'
        INDEPENDENT_DEMOCRAT = 'Independent Democrat'
        INDEPENDENT_REPUBLICAN = 'Independent Republican'
        INDEPENDENT_WHIG = 'Independent Whig'
        JACKSON = 'Jackson'
        JACKSON_DEMOCRAT = 'Jackson Democrat'
        JACKSON_FEDERALIST = 'Jackson Federalist'
        JACKSON_REPUBLICAN = 'Jackson Republican'
        JACKSONIAN = 'Jacksonian'
        JACKSONIAN_REPUBLICAN = 'Jacksonian Republican'
        LABOR = 'Labor'
        LAW_AND_ORDER = 'Law and Order'
        LIBERAL = 'Liberal'
        LIBERAL_REPUBLICAN = 'Liberal Republican'
        LIBERTY = 'Liberty'
        NA = 'NA'
        NACIONALISTA = 'Nacionalista'
        NATIONAL = 'National'
        NATIONAL_REPUBLICAN = 'National Republican'
        NEW_PROGRESSIVE = 'New Progressive'
        NONPARTISAN = 'Nonpartisan'
        NULLIFIER = 'Nullifier'
        OPPOSITION = 'Opposition'
        OPPOSITION_PARTY = 'Opposition Party'
        POPULIST = 'Populist'
        PRO_ADMINISTRATION = 'Pro-Administration'
        PROGRESISTA = 'Progresista'
        PROGRESSIVE = 'Progressive'
        PROGRESSIVE_REPUBLICAN = 'Progressive Republican'
        PROHIBITIONIST = 'Prohibitionist'
        READJUSTER = 'Readjuster'
        REPUBLICAN = 'Republican'
        SILVER_REPUBLICAN = 'Silver Republican'
        SOCIALIST = 'Socialist'
        STATE_RIGHTS_DEMOCRAT = 'State Rights Democrat'
        STATE_RIGHTS = 'States Rights'
        STATES_RIGHTS_DEMOCRAT = 'States Rights Democrat'
        STATES_RIGHTS_WHIG = 'States-Rights Whig'
        UNCONDITIONAL_UNIONIST = 'Unconditional Unionist'
        UNION = 'Union'
        UNION_LABOR = 'Union Labor'
        UNION_REPUBLICAN = 'Union Republican'
        UNIONIST = 'Unionist'
        UNKNOWN = 'Unknown'
        VAN_BUREN_DEMOCRAT = 'Van Buren Democrat'
        WHIG = 'Whig'


class State:
    """All states and territories, current and historical"""
    ALASKA = 'AK'
    ALABAMA = 'AL'
    ARKANSAS = 'AK'
    AMERICAN_SAMOA = 'AS'
    ARIZONA = 'AZ'
    CALIFORNIA = 'CA'
    COLORADO = 'CO'
    CONNETICUT = 'CT'
    DISTRICT_OF_COLUMBIA = 'DC'
    DELAWARE = 'DE'
    DAKOTA_TERRITORY = 'DK'
    FLORIDA = 'FL'
    GEORGIA = 'GA'
    GUAM = 'GU'
    HAWAII = 'HI'
    IOWA = 'IA'
    IDAHO = 'IN'
    KANSAS = 'KS'
    KENTUCKY = 'KY'
    LOUISIANA = 'LA'
    MASSACHUSETTS = 'MA'
    MARYLAND = 'MD'
    MAINE = 'ME'
    MICHIGAN = 'MI'
    MINNESOTA = 'MN'
    MISSOURI = 'MO'
    NORTHERN_MARIANA_ISLANDS = 'MP'
    MISSISSIPPI = 'MS'
    MONTANA = 'MN'
    NORTH_CAROLINA = 'NC'
    NORTH_DAKOTA = 'ND'
    NEBRASKA = 'NE'
    NEW_HAMPSHIRE = 'NH'
    NEW_JERSEY = 'NJ'
    NEW_MEXICO = 'NM'
    NEVADA = 'NV'
    NEW_YORK = 'NY'
    OHIO = 'OH'
    OKLAHOMA = 'OK'
    ORLEANS_TERRITORY = 'OL'
    OREGAN = 'OR'
    PENNSYLVANIA = 'PA'
    PHILIPPINE_ISLANDS = 'PI'
    PUERTO_RICO = 'PR'
    RHODE_ISLAND = 'RI'
    SOUTH_CAROLINA = 'SC'
    SOUTH_DAKOTA = 'SD'
    TENNESSEE = 'TN'
    TEXAS = 'TX'
    UTAH = 'UT'
    VIRGINIA = 'VA'
    VIRGIN_ISLANDS = 'VI'
    VERMONT = 'VT'
    WASHINGTON = 'WA'
    WISCONSIN = 'WI'
    WEST_VIRGINIA = 'WV'
    WYOMING = 'WY'
    UNITED_STATES = 'US'
