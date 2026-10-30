"""
Interactive visual 4-way road intersection renderer using clean scalable SVG.
"""
from typing import Dict, List, Optional
from src.models import Direction, SignalState, Vehicle, VehicleType
from src.queue_manager import IntersectionQueueManager


def render_intersection_svg(
    queue_mgr: IntersectionQueueManager,
    signal_states: Dict[str, SignalState],
    active_green_direction: Optional[Direction],
    green_duration: int = 0,
    departed_vehicles: Optional[List[Vehicle]] = None,
    sim_time: float = 0.0
) -> str:
    """
    Renders an SVG representation of the four-way road intersection.
    Includes roads, crosswalks, traffic lights with glow filters,
    directional queues with individual vehicle cards, and active departure indicators.
    """
    departed_count = len(departed_vehicles) if departed_vehicles else 0

    # Colors for vehicle types
    type_colors = {
        VehicleType.CAR: "#38BDF8",       # Sky blue
        VehicleType.BUS: "#F59E0B",       # Amber
        VehicleType.TRUCK: "#A855F7",     # Purple
        VehicleType.EMERGENCY: "#EF4444"  # Crimson Red
    }

    def get_signal_colors(direction: Direction):
        state = signal_states.get(direction.value, SignalState.RED)
        if state == SignalState.GREEN:
            return {"red": "#331111", "yellow": "#332200", "green": "#00E676", "glow": "url(#green-glow)"}
        elif state == SignalState.YELLOW:
            return {"red": "#331111", "yellow": "#FFC400", "green": "#003311", "glow": "url(#yellow-glow)"}
        else:
            return {"red": "#FF1744", "yellow": "#332200", "green": "#003311", "glow": "url(#red-glow)"}

    # Generate queued vehicle SVG elements for each approach
    # We display up to 6 vehicles graphically per queue with their IDs and badges
    def render_queue_vehicles(direction: Direction) -> str:
        q = queue_mgr.get_queue(direction)
        vehicles = q.get_vehicles()
        if not vehicles:
            return ""

        elements = []
        max_visible = 6
        shown = vehicles[:max_visible]

        for i, veh in enumerate(shown):
            color = type_colors.get(veh.vehicle_type, "#38BDF8")
            is_emg = veh.is_emergency
            stroke = "#FFFFFF" if is_emg else "none"
            stroke_width = "2" if is_emg else "0"

            # Compute coordinate based on direction
            if direction == Direction.NORTH:
                # Coming from top (y=0 to 230), in Southbound lane (x=275..335)
                # Front of queue is closest to stop line (y=220), subsequent vehicles further back
                vy = 205 - (i * 32)
                vx = 285
                w, h = 48, 24
                elements.append(f"""
                <g class="veh-group">
                    <rect x="{vx}" y="{vy}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"/>
                    <text x="{vx+24}" y="{vy+16}" fill="#FFFFFF" font-size="10" font-family="'JetBrains Mono', monospace" font-weight="bold" text-anchor="middle">{'🚨 ' if is_emg else ''}{veh.id.split('-')[-1]}</text>
                </g>
                """)
            elif direction == Direction.SOUTH:
                # Coming from bottom (y=470 to 700), in Northbound lane (x=365..425)
                # Front of queue is at y=475, subsequent further down
                vy = 472 + (i * 32)
                vx = 368
                w, h = 48, 24
                elements.append(f"""
                <g class="veh-group">
                    <rect x="{vx}" y="{vy}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"/>
                    <text x="{vx+24}" y="{vy+16}" fill="#FFFFFF" font-size="10" font-family="'JetBrains Mono', monospace" font-weight="bold" text-anchor="middle">{'🚨 ' if is_emg else ''}{veh.id.split('-')[-1]}</text>
                </g>
                """)
            elif direction == Direction.WEST:
                # Coming from left (x=0 to 230), in Eastbound lane (y=365..425)
                # Front of queue is at x=205, subsequent further left
                vx = 205 - (i * 32)
                vy = 368
                w, h = 24, 48
                elements.append(f"""
                <g class="veh-group">
                    <rect x="{vx}" y="{vy}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"/>
                    <text x="{vx+12}" y="{vy+28}" fill="#FFFFFF" font-size="9" font-family="'JetBrains Mono', monospace" font-weight="bold" text-anchor="middle">{'🚨' if is_emg else veh.id.split('-')[-1]}</text>
                </g>
                """)
            elif direction == Direction.EAST:
                # Coming from right (x=470 to 700), in Westbound lane (y=275..335)
                # Front of queue is at x=472, subsequent further right
                vx = 472 + (i * 32)
                vy = 285
                w, h = 24, 48
                elements.append(f"""
                <g class="veh-group">
                    <rect x="{vx}" y="{vy}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.5))"/>
                    <text x="{vx+12}" y="{vy+28}" fill="#FFFFFF" font-size="9" font-family="'JetBrains Mono', monospace" font-weight="bold" text-anchor="middle">{'🚨' if is_emg else veh.id.split('-')[-1]}</text>
                </g>
                """)

        # Add overflow indicator if queue > max_visible
        if len(vehicles) > max_visible:
            diff = len(vehicles) - max_visible
            if direction == Direction.NORTH:
                elements.append(f'<text x="310" y="25" fill="#FBBF24" font-size="12" font-weight="bold" text-anchor="middle">+{diff} more</text>')
            elif direction == Direction.SOUTH:
                elements.append(f'<text x="390" y="680" fill="#FBBF24" font-size="12" font-weight="bold" text-anchor="middle">+{diff} more</text>')
            elif direction == Direction.WEST:
                elements.append(f'<text x="25" y="395" fill="#FBBF24" font-size="12" font-weight="bold" text-anchor="middle">+{diff} more</text>')
            elif direction == Direction.EAST:
                elements.append(f'<text x="675" y="310" fill="#FBBF24" font-size="12" font-weight="bold" text-anchor="middle">+{diff} more</text>')

        return "\n".join(elements)

    north_sig = get_signal_colors(Direction.NORTH)
    south_sig = get_signal_colors(Direction.SOUTH)
    east_sig = get_signal_colors(Direction.EAST)
    west_sig = get_signal_colors(Direction.WEST)

    # Active center transit flow arrow and indicator
    center_indicator = ""
    if active_green_direction:
        dir_name = active_green_direction.value
        center_indicator = f"""
        <g id="center-flow-indicator">
            <rect x="295" y="295" width="110" height="110" rx="12" fill="rgba(0, 230, 118, 0.12)" stroke="#00E676" stroke-width="2" stroke-dasharray="6,4"/>
            <text x="350" y="340" fill="#00E676" font-size="14" font-weight="800" text-anchor="middle">ACTIVE GREEN</text>
            <text x="350" y="362" fill="#FFFFFF" font-size="18" font-family="'JetBrains Mono', monospace" font-weight="bold" text-anchor="middle">{dir_name}</text>
            <text x="350" y="385" fill="#9CA3AF" font-size="11" text-anchor="middle">{green_duration}s duration | {departed_count} served</text>
        </g>
        """

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 700" width="100%" height="640" style="background:#0F141E; border-radius:16px; box-shadow: 0 12px 36px rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.08);">
        <defs>
            <filter id="green-glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="red-glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="yellow-glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <!-- Grass / Terrain Corners -->
        <rect x="0" y="0" width="250" height="250" fill="#141C28" rx="8"/>
        <rect x="450" y="0" width="250" height="250" fill="#141C28" rx="8"/>
        <rect x="0" y="450" width="250" height="250" fill="#141C28" rx="8"/>
        <rect x="450" y="450" width="250" height="250" fill="#141C28" rx="8"/>

        <!-- Roads (Asphalt) -->
        <!-- Vertical Road -->
        <rect x="250" y="0" width="200" height="700" fill="#1C2331"/>
        <!-- Horizontal Road -->
        <rect x="0" y="250" width="700" height="200" fill="#1C2331"/>
        <!-- Center Intersection Box -->
        <rect x="250" y="250" width="200" height="200" fill="#222B3D"/>

        <!-- Curbs & Sidewalk borders -->
        <path d="M 250,0 L 250,250 L 0,250" stroke="#374151" stroke-width="4" fill="none"/>
        <path d="M 450,0 L 450,250 L 700,250" stroke="#374151" stroke-width="4" fill="none"/>
        <path d="M 250,700 L 250,450 L 0,450" stroke="#374151" stroke-width="4" fill="none"/>
        <path d="M 450,700 L 450,450 L 700,450" stroke="#374151" stroke-width="4" fill="none"/>

        <!-- Dashed Center Lane Dividers (Yellow) -->
        <line x1="350" y1="0" x2="350" y2="230" stroke="#FBBF24" stroke-width="3" stroke-dasharray="16,12"/>
        <line x1="350" y1="470" x2="350" y2="700" stroke="#FBBF24" stroke-width="3" stroke-dasharray="16,12"/>
        <line x1="0" y1="350" x2="230" y2="350" stroke="#FBBF24" stroke-width="3" stroke-dasharray="16,12"/>
        <line x1="470" y1="350" x2="700" y2="350" stroke="#FBBF24" stroke-width="3" stroke-dasharray="16,12"/>

        <!-- Stop Lines (Solid White) -->
        <!-- North incoming stop line -->
        <line x1="250" y1="235" x2="350" y2="235" stroke="#FFFFFF" stroke-width="6"/>
        <!-- South incoming stop line -->
        <line x1="350" y1="465" x2="450" y2="465" stroke="#FFFFFF" stroke-width="6"/>
        <!-- West incoming stop line -->
        <line x1="235" y1="350" x2="235" y2="450" stroke="#FFFFFF" stroke-width="6"/>
        <!-- East incoming stop line -->
        <line x1="465" y1="250" x2="465" y2="350" stroke="#FFFFFF" stroke-width="6"/>

        <!-- Zebra Crosswalks (Pedestrian safety marks) -->
        <!-- North Crosswalk -->
        <g stroke="#9CA3AF" stroke-width="4">
            <line x1="260" y1="242" x2="275" y2="242"/>
            <line x1="285" y1="242" x2="300" y2="242"/>
            <line x1="310" y1="242" x2="325" y2="242"/>
            <line x1="335" y1="242" x2="350" y2="242"/>
            <line x1="360" y1="242" x2="375" y2="242"/>
            <line x1="385" y1="242" x2="400" y2="242"/>
            <line x1="410" y1="242" x2="425" y2="242"/>
            <line x1="435" y1="242" x2="445" y2="242"/>
        </g>
        <!-- South Crosswalk -->
        <g stroke="#9CA3AF" stroke-width="4">
            <line x1="260" y1="458" x2="275" y2="458"/>
            <line x1="285" y1="458" x2="300" y2="458"/>
            <line x1="310" y1="458" x2="325" y2="458"/>
            <line x1="335" y1="458" x2="350" y2="458"/>
            <line x1="360" y1="458" x2="375" y2="458"/>
            <line x1="385" y1="458" x2="400" y2="458"/>
            <line x1="410" y1="458" x2="425" y2="458"/>
            <line x1="435" y1="458" x2="445" y2="458"/>
        </g>
        <!-- West Crosswalk -->
        <g stroke="#9CA3AF" stroke-width="4">
            <line x1="242" y1="260" x2="242" y2="275"/>
            <line x1="242" y1="285" x2="242" y2="300"/>
            <line x1="242" y1="310" x2="242" y2="325"/>
            <line x1="242" y1="335" x2="242" y2="350"/>
            <line x1="242" y1="360" x2="242" y2="375"/>
            <line x1="242" y1="385" x2="242" y2="400"/>
            <line x1="242" y1="410" x2="242" y2="425"/>
            <line x1="242" y1="435" x2="242" y2="445"/>
        </g>
        <!-- East Crosswalk -->
        <g stroke="#9CA3AF" stroke-width="4">
            <line x1="458" y1="260" x2="458" y2="275"/>
            <line x1="458" y1="285" x2="458" y2="300"/>
            <line x1="458" y1="310" x2="458" y2="325"/>
            <line x1="458" y1="335" x2="458" y2="350"/>
            <line x1="458" y1="360" x2="458" y2="375"/>
            <line x1="458" y1="385" x2="458" y2="400"/>
            <line x1="458" y1="410" x2="458" y2="425"/>
            <line x1="458" y1="435" x2="458" y2="445"/>
        </g>

        <!-- APPROACH LABELS & STATS -->
        <!-- North -->
        <g>
            <rect x="25" y="15" width="200" height="70" rx="8" fill="rgba(17,24,39,0.85)" stroke="#374151"/>
            <text x="35" y="40" fill="#00F2FE" font-size="14" font-weight="bold">NORTH APPROACH</text>
            <text x="35" y="60" fill="#9CA3AF" font-size="11">Queue: <tspan fill="#FFFFFF" font-weight="bold">{len(queue_mgr.get_queue(Direction.NORTH))}</tspan> veh | Avg Wait: <tspan fill="#FFFFFF">{queue_mgr.get_queue(Direction.NORTH).average_waiting_time(sim_time):.1f}s</tspan></text>
            <text x="35" y="75" fill="#EF4444" font-size="10" font-weight="bold">{'🚨 EMERGENCY WAITING' if queue_mgr.get_queue(Direction.NORTH).has_emergency() else ''}</text>
        </g>
        <!-- East -->
        <g>
            <rect x="475" y="15" width="200" height="70" rx="8" fill="rgba(17,24,39,0.85)" stroke="#374151"/>
            <text x="485" y="40" fill="#00F2FE" font-size="14" font-weight="bold">EAST APPROACH</text>
            <text x="485" y="60" fill="#9CA3AF" font-size="11">Queue: <tspan fill="#FFFFFF" font-weight="bold">{len(queue_mgr.get_queue(Direction.EAST))}</tspan> veh | Avg Wait: <tspan fill="#FFFFFF">{queue_mgr.get_queue(Direction.EAST).average_waiting_time(sim_time):.1f}s</tspan></text>
            <text x="485" y="75" fill="#EF4444" font-size="10" font-weight="bold">{'🚨 EMERGENCY WAITING' if queue_mgr.get_queue(Direction.EAST).has_emergency() else ''}</text>
        </g>
        <!-- South -->
        <g>
            <rect x="475" y="615" width="200" height="70" rx="8" fill="rgba(17,24,39,0.85)" stroke="#374151"/>
            <text x="485" y="640" fill="#00F2FE" font-size="14" font-weight="bold">SOUTH APPROACH</text>
            <text x="485" y="660" fill="#9CA3AF" font-size="11">Queue: <tspan fill="#FFFFFF" font-weight="bold">{len(queue_mgr.get_queue(Direction.SOUTH))}</tspan> veh | Avg Wait: <tspan fill="#FFFFFF">{queue_mgr.get_queue(Direction.SOUTH).average_waiting_time(sim_time):.1f}s</tspan></text>
            <text x="485" y="675" fill="#EF4444" font-size="10" font-weight="bold">{'🚨 EMERGENCY WAITING' if queue_mgr.get_queue(Direction.SOUTH).has_emergency() else ''}</text>
        </g>
        <!-- West -->
        <g>
            <rect x="25" y="615" width="200" height="70" rx="8" fill="rgba(17,24,39,0.85)" stroke="#374151"/>
            <text x="35" y="640" fill="#00F2FE" font-size="14" font-weight="bold">WEST APPROACH</text>
            <text x="35" y="660" fill="#9CA3AF" font-size="11">Queue: <tspan fill="#FFFFFF" font-weight="bold">{len(queue_mgr.get_queue(Direction.WEST))}</tspan> veh | Avg Wait: <tspan fill="#FFFFFF">{queue_mgr.get_queue(Direction.WEST).average_waiting_time(sim_time):.1f}s</tspan></text>
            <text x="35" y="675" fill="#EF4444" font-size="10" font-weight="bold">{'🚨 EMERGENCY WAITING' if queue_mgr.get_queue(Direction.WEST).has_emergency() else ''}</text>
        </g>

        <!-- TRAFFIC SIGNAL POSTS (4 HEADS) -->
        <!-- North Signal (placed near corner top-left of junction) -->
        <g transform="translate(205, 175)">
            <rect width="28" height="66" rx="6" fill="#111827" stroke="#374151" stroke-width="2"/>
            <circle cx="14" cy="14" r="8" fill="{north_sig['red']}" filter="{north_sig['glow'] if north_sig['red'] == '#FF1744' else 'none'}"/>
            <circle cx="14" cy="33" r="8" fill="{north_sig['yellow']}" filter="{north_sig['glow'] if north_sig['yellow'] == '#FFC400' else 'none'}"/>
            <circle cx="14" cy="52" r="8" fill="{north_sig['green']}" filter="{north_sig['glow'] if north_sig['green'] == '#00E676' else 'none'}"/>
        </g>

        <!-- East Signal (placed near corner top-right of junction) -->
        <g transform="translate(460, 185) rotate(90)">
            <rect width="28" height="66" rx="6" fill="#111827" stroke="#374151" stroke-width="2"/>
            <circle cx="14" cy="14" r="8" fill="{east_sig['red']}" filter="{east_sig['glow'] if east_sig['red'] == '#FF1744' else 'none'}"/>
            <circle cx="14" cy="33" r="8" fill="{east_sig['yellow']}" filter="{east_sig['glow'] if east_sig['yellow'] == '#FFC400' else 'none'}"/>
            <circle cx="14" cy="52" r="8" fill="{east_sig['green']}" filter="{east_sig['glow'] if east_sig['green'] == '#00E676' else 'none'}"/>
        </g>

        <!-- South Signal (placed near corner bottom-right of junction) -->
        <g transform="translate(465, 460)">
            <rect width="28" height="66" rx="6" fill="#111827" stroke="#374151" stroke-width="2"/>
            <circle cx="14" cy="14" r="8" fill="{south_sig['red']}" filter="{south_sig['glow'] if south_sig['red'] == '#FF1744' else 'none'}"/>
            <circle cx="14" cy="33" r="8" fill="{south_sig['yellow']}" filter="{south_sig['glow'] if south_sig['yellow'] == '#FFC400' else 'none'}"/>
            <circle cx="14" cy="52" r="8" fill="{south_sig['green']}" filter="{south_sig['glow'] if south_sig['green'] == '#00E676' else 'none'}"/>
        </g>

        <!-- West Signal (placed near corner bottom-left of junction) -->
        <g transform="translate(240, 480) rotate(-90)">
            <rect width="28" height="66" rx="6" fill="#111827" stroke="#374151" stroke-width="2"/>
            <circle cx="14" cy="14" r="8" fill="{west_sig['red']}" filter="{west_sig['glow'] if west_sig['red'] == '#FF1744' else 'none'}"/>
            <circle cx="14" cy="33" r="8" fill="{west_sig['yellow']}" filter="{west_sig['glow'] if west_sig['yellow'] == '#FFC400' else 'none'}"/>
            <circle cx="14" cy="52" r="8" fill="{west_sig['green']}" filter="{west_sig['glow'] if west_sig['green'] == '#00E676' else 'none'}"/>
        </g>

        <!-- QUEUED VEHICLES -->
        {render_queue_vehicles(Direction.NORTH)}
        {render_queue_vehicles(Direction.SOUTH)}
        {render_queue_vehicles(Direction.EAST)}
        {render_queue_vehicles(Direction.WEST)}

        <!-- Active Center Flow Indicator -->
        {center_indicator}
    </svg>
    """
    return svg
