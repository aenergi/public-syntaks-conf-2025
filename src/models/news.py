from enum import Enum
from typing import List
from pydantic import BaseModel, Field, field_validator


class NyhetsTema(Enum):
    """En modell som representerer tema for en nyhetssak."""
    POLITIKK = "Politikk"  # Saken handler om politikk, f.eks. valg, regjering, lover og regler
    SAMFUNN = "Samfunn"  # Saken handler om samfunnsforhold, f.eks. sosiale forhold, kultur og utdanning
    ØKONOMI = "Økonomi"  # Saken handler om økonomi, f.eks. aksjemarkedet, arbeidsledighet og inflasjon
    UTDANNING = "Utdanning"  # Saken handler om utdanning, f.eks. skoler, universiteter og utdanningssystemet
    HELSE = "Helse"  # Saken handler om helse, f.eks. sykdommer, behandling og helsevesenet
    MILJØ = "Miljø"  # Saken handler om miljø, f.eks. klimaendringer, forurensning og naturkatastrofer
    KULTUR = "Kultur"  # Saken handler om kultur, f.eks. kunst, musikk og litteratur
    SPORT = "Sport"  # Saken handler om sport, f.eks. idrett, konkurranser og utøvere
    TEKNOLOGI = "Teknologi"  # Saken handler om teknologi, f.eks. innovasjoner, forskning og utvikling
    UNDERHOLDNING = "Underholdning"  # Saken handler om underholdning, f.eks. filmer, TV-serier og kjendiser
    REISE = "Reise"  # Saken handler om reise, f.eks. reisemål, reiseopplevelser og reisetips
    ANNET = "Annet"  # Saken handler om annet, f.eks. saker som ikke passer inn i de andre kategoriene


class NyhetsObjekt(BaseModel):
    """En modell som beskriver objektene i en nyhetssak."""
    type: str  # Type objekt, f.eks. "Person", "Organisasjon", "Sted", "Hendelse"
    navn: str  # Navn på objektet, f.eks. navn på personer, organisasjoner, steder eller hendelser


class NyhetsSentiment(Enum):
    """En modell som representerer sentiment i en nyhetssak."""
    POSITIVT = "Positivt"  # Positivt sentiment sier at saken er positivt vinklet
    NEGATIVT = "Negativt"  # Negativt sentiment sier at saken er negativt vinklet
    NØYTRALT = "Nøytralt"  # Nøytralt sentiment sier at saken er nøytral, f.eks. nyhetssaker uten klar vinkling eller mening


class NyhetsAlvorlighetsgrad(Enum):
    """En modell som representerer alvorlighetsgrad i en nyhetssak."""
    LAV = "Lav"  # En lav alvorlighetsgrad kan være nyhetssaker som ikke er så viktige eller har liten innvirkning på samfunnet, f.eks. underholdning
    MODERAT = "Moderat"  # En moderat alvorlighetsgrad kan være nyhetssaker som har en viss innvirkning på samfunnet, f.eks. lokale hendelser eller mindre politiske saker
    HØY = "Høy"  # En høy alvorlighetsgrad kan være nyhetssaker som har stor innvirkning på samfunnet, f.eks. politiske hendelser eller naturkatastrofer
    KRITISK = "Kritisk"  # En kritisk alvorlighetsgrad kan være nyhetssaker som har ekstremt stor innvirkning på samfunnet, f.eks. krig eller terrorangrep


class NyhetsMålgruppe(Enum):
    """En modell som representerer målgruppen for en nyhetssak."""
    BARN = "Barn"  # Nyhetssaken er rettet mot barn
    UNGDOM = "Ungdom"  # Nyhetssaken er rettet mot ungdom
    VOKSNE = "Voksne"  # Nyhetssaken er rettet mot voksne
    ELDRE = "Eldre"  # Nyhetssaken er rettet mot eldre
    ANNET = "Annet"  # Nyhetssaken er rettet mot annet


class NyhetsClickbait(BaseModel):
    """En modell som representerer clickbait i en nyhetssak. 
    Hvor clickbait betyr at overskriften er laget for å tiltrekke seg klikk, og gjerne overdriver eller misrepresenterer innholdet i saken."""
    clickbait: bool  # True hvis saken inneholder clickbait, False hvis ikke
    clickbait_score: float  # Score fra 0-1 som angir hvor mye clickbait saken inneholder
    clickbait_text: str  # Tekst som angir hva som er clickbait i saken


class Nyhet(BaseModel):
    """En modell som representerer en nyhetssak."""
    tema: List[NyhetsTema] = Field(description="Tema for nyhetssaken")
    objekt: List[NyhetsObjekt] = Field(description="Objekter i nyhetssaken")
    sentiment: NyhetsSentiment = Field(description="Sentiment i nyhetssaken")
    alvorlighetsgrad: NyhetsAlvorlighetsgrad = Field(description="Alvorlighetsgrad i nyhetssaken")
    målgruppe: List[NyhetsMålgruppe] = Field(description="Målgruppe for nyhetssaken")
    clickbait: NyhetsClickbait = Field(description="Clickbait i nyhetssaken")

    @field_validator("tema", mode="before")
    def validate_tema(cls, v):
        if not isinstance(v, list):
            raise ValueError("Tema must be a list")
        return v


class ClusterInfo(BaseModel):
    """En modell som representerer informasjon om en gruppe nyhetssaker."""
    tittel: str = Field(description="Tittel på gruppen av nyhetssaker")
    sammendrag: str = Field(description="Kort sammendrag av gruppen nyhetssaker")