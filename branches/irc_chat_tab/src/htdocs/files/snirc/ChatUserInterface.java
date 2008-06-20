

import java.awt.*;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;

/**
 * <p>Responsible for setting up and maintaining the User Interface of the Applet.
 *
 * @version $Id: ChatUserInterface.java,v 1.8 2004/07/26 18:24:58 bryan_w Exp $
 */

public class ChatUserInterface extends Panel {
    /** Default background colour of the applet's widgets */
    public final static Color BACKGROUND_COLOUR = Color.white;
    /** Default foreground colour of the applet's widgets */
    public final static Color FOREGROUND_COLOUR = Color.black;
    /** Version number for the applet, and supporting code */


    private Panel buttonBar;
    private Label channelLabel = new Label("                    ", Label.LEFT);
    private Label nickLabel = new Label("                    ", Label.LEFT);
    private Button nickButton;
    private PopupMenu nickListMenu;
    private List nickList = new List(19, false);
    private TextField userMsg = new TextField(70);
    private Label lblTopic = new Label("");
    private Panel topline;
    private CheckboxMenuItem chkJoinPart;
    private static CheckboxMenuItem chkShowPingPong;
    private ScrollableOutputPanel outputPanel;
    private Button channelButton;
    private ActionListener menusAndButtonsListener;
    private boolean allowChannelChange = true;
    

    private MouseListener mouseEventHandler = new MouseAdapter() {
        public void mouseReleased(MouseEvent e) {
            if (e.isPopupTrigger()) {
                nickListMenu.show(nickList, e.getX(), e.getY());
            }
        }

        public void mousePressed(MouseEvent e) {
            if (e.isPopupTrigger()) {
                nickListMenu.show(nickList, e.getX(), e.getY());
            }
        }
    };

    /**
     * Initializes up the User Interface.
     */
    public ChatUserInterface(ActionListener userInputListener,
                             ActionListener menusAndButtonsListener,
                             boolean defaultHideJoinsAndParts,
                             boolean bareBones,
                             boolean allowChannelChange,
                             Font defaultFont) {
        this.allowChannelChange = allowChannelChange;
        setFont(defaultFont);
        this.menusAndButtonsListener = menusAndButtonsListener;
        outputPanel = new ScrollableOutputPanel();
        setLayout(new BorderLayout());

        Panel msgline = new Panel();
        msgline.setLayout(new FlowLayout(FlowLayout.LEFT));
        msgline.add(userMsg);
        userMsg.addActionListener(userInputListener);
        msgline.add(new Label(Chat.VERSION));

        nickList.addMouseListener(mouseEventHandler);
        nickList.setMultipleMode(false);
        nickListMenu = createContextMenu();
        this.add(nickListMenu);
        chkJoinPart.setState(defaultHideJoinsAndParts);

        // top panel controls
        topline = new Panel();
        topline.setLayout(new BorderLayout());

        if (!bareBones) {
            createButtonBar();
        }
        topline.add("Center", lblTopic);

        add("North", topline);
        add("South", msgline);
        add("East", nickList);
        add("Center", outputPanel);
    }

    private void createButtonBar() {
        buttonBar = new Panel();
        buttonBar.setLayout(new FlowLayout(FlowLayout.LEFT));
        nickButton = createButton("Nick");
        buttonBar.add(nickButton);
        buttonBar.add(nickLabel);
        channelButton = createButton("Channel");
        buttonBar.add(channelButton);
        buttonBar.add(channelLabel);
        buttonBar.add(createButton("Help"));
        buttonBar.add(createButton("List"));
        topline.add("North", buttonBar);
        nickButton.setEnabled(false);
        channelButton.setEnabled(false);
        outputPanel.setChatFont(getFont());
        setBackground(BACKGROUND_COLOUR);
        setForeground(FOREGROUND_COLOUR);
        setFontAndColours(nickList);
        setFontAndColours(userMsg);
        setFontAndColours(nickLabel);
        setFontAndColours(channelLabel);
    }

    /**
     * Once the connection to the IRC server has been established, this method is called
     * to prepare the User Interface for user interaction.
     */
    public void makeReadyForCommands(boolean bareBones) {
	if(!bareBones) {
            nickButton.setEnabled(true);
	    channelButton.setEnabled(allowChannelChange);
	}
        userMsg.requestFocus();
    }

    /**
     * Return the currently displayed channel name
     */
    public String getChannelName() {
        return channelLabel.getText();
    }

    /**
     * Return the currently displayed nick
     */
    public String getNick() {
        return nickLabel.getText();
    }

    /**
     * Return the List that contains the nicks currently on the channel, prefixed
     * with the appropriate "status" character, @ + or a space depending on the
     * status. The contents of the list are manipulated by the Chat.
     *
     * <p>This is deliberately bad design - the alternative would bloat the size
     * of the applet significantly, and the gain in code clarity wouldn't be worth it.
     */
    public List getNickList() {
        return nickList;
    }

    /**
     * Return the currently selected nickname from the channel nick-list.
     */
    public String getSelectedNick() {
        String selectedNick = nickList.getSelectedItem();
        return selectedNick == null ? null : selectedNick.substring(1);
    }
    
    /**
     * Returns the index of the currently selected nickname from the channel nick-list
     */
     public int getSelectedNickIndex(){
     	// Stubby!
     	return 0;
     }
     	

    /**
     * Return whether the user has opted to display joins and
     * parts.
     */
    public boolean isDisplayingJoinsAndParts() {
        return chkJoinPart.getState();
    }
    
    /**
     * Returns whether the user has opted to display ping pong 
     * events
     */
     public static boolean isDisplayingPingAndPong() {
     	return chkShowPingPong.getState();
     }

    /**
     * Set the currently-displayed channel name
     */
    public void setChannelName(String channel) {
        channelLabel.setText(channel);
    }

    /**
     * Set the currently-displayed nick
     */
    public void setNick(String nick) {
        nickLabel.setText(nick);
    }

    /**
     * Set the currently displayed channel topic
     */
    public void setTopic(String topic) {
    	boolean reTypeTopic = true;
    	if (reTypeTopic){
        	lblTopic.setText("Topic: " + topic);
        	reTypeTopic = false;
        }
        else
        	lblTopic.setText(topic);
    }
  

    /**
     * Append a line to the output area. The argument should not end with a newline.
     */
    public void appendOutputLine(String line) {
        outputPanel.appendLine(line);
    }

    private void setFontAndColours(Component c) {
        c.setFont(getFont());
        c.setBackground(BACKGROUND_COLOUR);
        c.setForeground(FOREGROUND_COLOUR);
    }

    private Button createButton(String text) {
        Button button = new Button(text);
        button.addActionListener(menusAndButtonsListener);
        return button;
    }

    private PopupMenu createContextMenu() {
        MenuItem item;
        PopupMenu menu = new PopupMenu();

        menu.add(createMenuItem("Whois"));
        menu.addSeparator();
        menu.add(createMenuItem("Ignore"));
        menu.add(createMenuItem("View Ignore List"));
        menu.addSeparator();
        
        Menu mnuOp = new Menu("Op Options");
        mnuOp.add(createMenuItem("Give Ops"));
        mnuOp.add(createMenuItem("Take Ops"));
        mnuOp.addSeparator();
        mnuOp.add(createMenuItem("Give Voice"));
        mnuOp.add(createMenuItem("Take Voice"));
        mnuOp.addSeparator();
        mnuOp.add(createMenuItem("Kick"));
        mnuOp.add(createMenuItem("Ban")); 
        menu.add(mnuOp);

        Menu mnuCTCP = new Menu("CTCP");
        mnuCTCP.add(createMenuItem("Version"));
        mnuCTCP.add(createMenuItem("Ping"));
        menu.add(mnuCTCP);

        Menu mnuProperties = new Menu("Properties");
        chkJoinPart = new CheckboxMenuItem("Show Joins/Parts/Quits");
        mnuProperties.add(chkJoinPart);
        chkShowPingPong = new CheckboxMenuItem("Show Ping? Pong! Event");
        mnuProperties.add(chkShowPingPong);
        chkShowPingPong.setState(true);
    
        mnuProperties.addSeparator();
        mnuProperties.add(createMenuItem("Refresh"));
        menu.add(mnuProperties);

        menu.addSeparator();
        menu.add(createMenuItem("About"));

        return menu;
    }

    private MenuItem createMenuItem(String title) {
        MenuItem item = new MenuItem(title);
        item.addActionListener(menusAndButtonsListener);
        return item;
    }

}
